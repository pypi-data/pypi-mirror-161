# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import uuid
import logging
from ._authentication._authentication import get_switch_credentials
from ._utils._utils import ApiInputs, ApiHeaders
from ._utils._constants import SWITCH_ENVIRONMENT

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler(stream=sys.stdout)
# consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


def initialize(api_project_id: uuid.UUID, environment: SWITCH_ENVIRONMENT = 'Production') -> ApiInputs:
    """
    Initialize session with API when running scripts on your local machine.

    Parameters
    ----------
    api_project_id : uuid.UUID
        The ApiProjectID for the portfolio.
    environment: SWITCH_ENVIRONMENT
        (Optional) The Switch API environment to interact with

    Returns
    -------
    ApiInputs
        Returns the ApiInputs namedtuple that is required as an input to other functions.
    """

    try:
        uuid.UUID(api_project_id)
    except:
        sw.logger.error(f"Invalid value provided '{api_project_id}'- please provide a valid api_project_id. ")
        return False

    creds = get_switch_credentials(environment, api_project_id)

    logger.info("Successfully initialized.")
    api_base_url = f"https://{creds.api_endpoint}/api/1.0"
    # api_base_url = f"https://localhost:5001/api/1.0"
    api_projects_endpoint = f"{api_base_url}/projects"

    token = creds.api_token

    data_feed_id = '00000000-0000-0000-0000-000000000000'
    data_feed_file_status_id = '00000000-0000-0000-0000-000000000000'

    api_default = {
        'Content-Type': 'application/json; charset=utf-8',
        'Ocp-Apim-Subscription-Key': creds.subscription_key,
        'Authorization': f'bearer {token}'
    }

    operation_metadata = {
        'DataFeedId': data_feed_id,
        'DataFeedFileStatusId': data_feed_file_status_id
    }

    # API Header specific for Integration API endpoints
    api_integration = {
        'Content-Type': 'application/json; charset=utf-8',
        'Ocp-Apim-Subscription-Key': creds.subscription_key,
        'Authorization': f'bearer {token}',
        'X-Operation-Metadata': str(operation_metadata)
    }

    api_headers = ApiHeaders(default=api_default, integration=api_integration)

    return ApiInputs(email_address=creds.email, user_id=creds.user_id, api_project_id=api_project_id,
                     data_feed_id=data_feed_id, data_feed_file_status_id=data_feed_file_status_id, bearer_token=token,
                     api_base_url=api_base_url, api_projects_endpoint=api_projects_endpoint,
                     subscription_key=creds.subscription_key, api_headers=api_headers)
