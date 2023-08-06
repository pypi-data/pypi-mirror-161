# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import sys
from uuid import UUID
from msal.oauth2cli.oidc import decode_id_token
import requests
from ._credentials_store._credentials_store import SwitchCredentials, store_credentials
from ._credentials_store._credentials_store import read_credentials
from ._msal._custom_application import CustomPublicClientApplication
from .._utils._constants import AUTH_ENDPOINT_DEV, AUTH_ENDPOINT_PROD, SWITCH_ENVIRONMENT

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


_authority = {
  "dev": {
    "uitemplateid": "dev",
    "base_url": "https://switchdevb2c.b2clogin.com/switchdevb2c.onmicrosoft.com",
  },
  "prod": {
    "base_url": "https://switchautomation.b2clogin.com/switchautomation.onmicrosoft.com",
    "uitemplateid": "default"
  }
}


def _validate_credentials(creds: SwitchCredentials, version: str):
    """Validate given Credentials

    Ensures that credentials are up to date and synced.

    Parameters
    ----------
    creds
        SwitchCredentials to validate
    version
        The Credentials version

    Returns
    -------
    bool
        Returns the True when credentials are valid; otherwise returns False

    """

    if creds is None or creds is False or creds.user_id == '' or creds.user_id is None or creds.api_token is None:
        return False

    if creds.version != version:
        return False

    try:
        decode_id_token(creds.api_token)
        return True
    except Exception as ex:
        logger.info('Cached token expired. Requesting login.')
        return False


def get_switch_credentials(environment: SWITCH_ENVIRONMENT, portfolio_id):
    """Read Credentials

    Reads credentials from credential store

    Parameters
    ----------
    environment
        Either development or production environment
    portfolio_id
        Get credentials for the given portfolio id

    Returns
    -------
    SwitchCredentials
        Returns the SwitchCredentials namedtuple containing credentials to call Switch APIs

    """

    login_context = fetch_login_context(environment=environment, api_project_id=portfolio_id)[1]

    # Fetch from credentials store if it's already been cached
    if login_context is not None:
        datacenter = login_context['dataCenter']
        key_prefix = f"{environment}_{datacenter}" if environment == 'Development' else datacenter
        cur_credentials = read_credentials(key_prefix, login_context['portfolioId'], login_context['portfolioName'])
        if _validate_credentials(cur_credentials, login_context['version']):
            return cur_credentials
    else:
        raise Exception('Unable to obtain Login Context to authenticate with Switch Automation. '
                        'Please contact your administrator.')

    # Credentials do not exist, take user through browser auth journey
    config_env = 'dev' if environment == 'Development' else 'prod'
    authority = f"{_authority[config_env]['base_url']}/{login_context['policyName']}"
    app = CustomPublicClientApplication(login_context['applicationId'], authority=authority)

    uitemplateid = _authority[config_env]['uitemplateid']
    prompt = login_context['prompt'] if login_context['prompt'] != '' else None
    auth_response = app.acquire_token_interactive_custom(scopes=[], prompt=prompt, port=51796,
                                                         auth_params={
                                                             "uitemplateid": uitemplateid,
                                                             "portfolioId": portfolio_id,
                                                             "environment": environment
    })

    id_token = auth_response['id_token']

    api_base_url = AUTH_ENDPOINT_DEV if environment == 'Development' else AUTH_ENDPOINT_PROD
    _, profile = fetch_user_profile_details(api_base_url, id_token, environment, portfolio_id)

    if profile is None:
        raise Exception('Unable to obtain User Profile. Please try again or contact your administrator.')

    credentials = SwitchCredentials(login_context['version'], profile['email'],
                                    profile['userId'], login_context['portfolioId'],
                                    login_context['portfolioName'], id_token, profile['apiEndpoint'],
                                    environment, profile['subscriptionKey'])

    store_credentials(credentials, key_prefix=key_prefix)

    return credentials


def fetch_user_profile_details(api_base_url: str, token: str, environment: SWITCH_ENVIRONMENT, api_project_id: UUID):
    """
    Fetch User Profile details with respect to the given environment and portfolio

    Parameters
    ----------
    api_base_url
        User Profile base url
    token
        Switch token for authentication
    environment
        Either development or production environment
    api_project_id
        Get UserProfile with respect to this portfolio id

    Returns
    -------
    tuple[str, any]
        Returns the User Profile details containing information to call Switch APIs
    """

    payload = {}
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'bearer {token}'
    }

    url = f"{api_base_url}/user-profile?portfolioId={api_project_id}&switchEnvironment={environment}"

    response = requests.request("GET", url, data=payload, timeout=20, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, None
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, None
    return response_status, response.json()


def fetch_login_context(environment: SWITCH_ENVIRONMENT, api_project_id: UUID):
    """
    Fetches login context to assist SSO with Switch Platform

    Parameters
    ----------
    environment
        Either development or production environment
    api_project_id
        Get UserProfile with respect to this portfolio id

    Returns
    -------
    tuple[str, any]
        Returns the Login Context containing information to authenticate with Switch
    """

    base_url = AUTH_ENDPOINT_DEV if environment == 'Development' else AUTH_ENDPOINT_PROD

    payload = {}
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }

    url = f"{base_url}/login-context?portfolioId={api_project_id}&switchEnvironment={environment}&type=PyPkg"

    response = requests.request("GET", url, data=payload, timeout=20, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)
    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, None
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return response_status, None
    return response_status, response.json()
