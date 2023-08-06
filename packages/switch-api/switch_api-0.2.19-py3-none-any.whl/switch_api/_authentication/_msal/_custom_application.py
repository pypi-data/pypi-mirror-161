# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import logging
import os
import sys
from typing import Optional, List

from msal import PublicClientApplication

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  %(name)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


def _merge_claims_challenge_and_capabilities(capabilities, claims_challenge):
    """
    Represent capabilities as {"access_token": {"xms_cc": {"values": capabilities}}} and then merge/add it into
    incoming claims
    """
    if not capabilities:
        return claims_challenge
    claims_dict = json.loads(claims_challenge) if claims_challenge else {}
    for key in ["access_token"]:  # We could add "id_token" if we'd decide to
        claims_dict.setdefault(key, {}).update(xms_cc={"values": capabilities})
    return json.dumps(claims_dict)


def _clean_up(result):
    if isinstance(result, dict):
        result.pop("refresh_in", None)  # MSAL handled refresh_in, customers need not
    return result


def _preferred_browser():
    """Register Edge and return a name suitable for subsequent webbrowser.get(...)
    when appropriate. Otherwise return None.
    """
    # On Linux, only Edge will provide device-based Conditional Access support
    if sys.platform != "linux":  # On other platforms, we have no browser preference
        return None
    browser_path = "/usr/bin/microsoft-edge"  # Use a full path owned by sys admin
    user_has_no_preference = "BROWSER" not in os.environ
    user_wont_mind_edge = "microsoft-edge" in os.environ.get("BROWSER", "")  # Note:
    # BROWSER could contain "microsoft-edge" or "/path/to/microsoft-edge".
    # Python documentation (https://docs.python.org/3/library/webbrowser.html)
    # does not document the name being implicitly register,
    # so there is no public API to know whether the ENV VAR browser would work.
    # Therefore, we would not bother examine the env var browser's type.
    # We would just register our own Edge instance.
    if (user_has_no_preference or user_wont_mind_edge) and os.path.exists(browser_path):
        try:
            import webbrowser  # Lazy import. Some distro may not have this.
            browser_name = "msal-edge"  # Avoid popular name "microsoft-edge"
            # otherwise `BROWSER="microsoft-edge"; webbrowser.get("microsoft-edge")`
            # would return a GenericBrowser instance which won't work.
            try:
                registration_available = isinstance(
                    webbrowser.get(browser_name), webbrowser.BackgroundBrowser)
            except webbrowser.Error:
                registration_available = False
            if not registration_available:
                logger.debug("Register %s with %s", browser_name, browser_path)
                # By registering our own browser instance with our own name,
                # rather than populating a process-wide BROWSER enn var,
                # this approach does not have side effect on non-MSAL code path.
                webbrowser.register(  # Even double-register happens to work fine
                    browser_name, None, webbrowser.BackgroundBrowser(browser_path))
            return browser_name
        except ImportError:
            pass  # We may still proceed
    return None


class CustomPublicClientApplication(PublicClientApplication):
    """
    Extends Msal PublicClientApplication to support custom Query Parameters.
    Future: Request feature in python msal GitHub
    """

    def __init__(self, client_id, client_credential=None, **kwargs):
        if client_credential is not None:
            raise ValueError("Public Client should not possess credentials")
        super(PublicClientApplication, self).__init__(
            client_id, client_credential=None, **kwargs)

    def acquire_token_interactive_custom(self, scopes: List[str], prompt=None, login_hint: str=None,
                                         domain_hint: str=None, claims_challenge: str=None, timeout: int=None,
                                         port: int=None, extra_scopes_to_consent=None, auth_params: dict=None, **kwargs):
        """Acquire token interactively i.e. via a local browser.
        Overridden to support custom query parameters.

        Prerequisite: In Azure Portal, configure the Redirect URI of your
        "Mobile and Desktop application" as ``http://localhost``.

        Parameters
        ----------
        scopes : List[str]
            It is a list of case-sensitive strings.
        prompt : str
            By default, no prompt value will be sent, not even "none". You will have to specify a value explicitly. Its
            valid values are defined in Open ID Connect specs
            https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        login_hint : str
            Identifier of the user. Generally a User Principal Name (UPN) (Default value = None).
        domain_hint : str
            Can be one of "consumers" or "organizations" or your tenant domain "contoso.com". If included, it will skip
            the email-based discovery process that user goes through on the sign-in page, leading to a slightly more
            streamlined user experience. More information on possible values:
            `here <https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#request-an-
            authorization-code>`_ and
            `here <https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-oapx/
            86fb452d-e34a-494e-ac61-e526e263b6d8>`_.  (Default value = None)
        claims_challenge : str
            The claims_challenge parameter requests specific claims requested by the resource provider in the form of a
            claims_challenge directive in the www-authenticate header to be returned from the UserInfo Endpoint and/or
            in the ID Token and/or Access Token. It is a string of a JSON object which contains lists of claims being
            requested from these locations (Default value = None).
        timeout : int
            This method will block the current thread. This parameter specifies the timeout value in seconds. Default
            value ``None`` means wait indefinitely.
        port : int
            The port to be used to listen to an incoming auth response.
            By default we will use a system-allocated port.
            (The rest of the redirect_uri is hard coded as ``http://localhost``.)
        extra_scopes_to_consent : list
            "Extra scopes to consent" is a concept only available in AAD. It refers to other resources you might want
            to prompt to consent for, in the same interaction, but for which you won't get back a token for in this
            particular operation.
        auth_params : dict
            "Additional Auth Query Params to be sent to STS"

        Returns
        -------
        dict
            A dict containing no "error" key, and typically contains an "access_token" key. A dict containing an
            "error" key, when token refresh failed.

        """
        self._validate_ssh_cert_input_data(kwargs.get("data", {}))
        claims = _merge_claims_challenge_and_capabilities(
            self._client_capabilities, claims_challenge)
        telemetry_context = self._build_telemetry_context(
            self.ACQUIRE_TOKEN_INTERACTIVE)

        auth_params['claims'] = claims
        auth_params['domain_hint'] = domain_hint

        response = _clean_up(self.client.obtain_token_by_browser(
            scope=self._decorate_scope(scopes) if scopes else None,
            extra_scope_to_consent=extra_scopes_to_consent,
            redirect_uri="http://localhost:{port}".format(
                # Hardcode the host, for now. AAD portal rejects 127.0.0.1 anyway
                port=port or 0),
            prompt=prompt,
            login_hint=login_hint,
            timeout=timeout,
            auth_params=auth_params,
            data=dict(kwargs.pop("data", {}), claims=claims),
            headers=telemetry_context.generate_headers(),
            browser_name=_preferred_browser(),
            **kwargs))
        telemetry_context.update_telemetry(response)
        return response
