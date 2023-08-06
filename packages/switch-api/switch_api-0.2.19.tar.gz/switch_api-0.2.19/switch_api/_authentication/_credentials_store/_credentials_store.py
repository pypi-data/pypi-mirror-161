# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from collections import namedtuple
from os import path
from uuid import UUID

cred_filename = '.env'

SwitchCredentials = namedtuple('SwitchCredentials', ['version', 'email', 'user_id', 'portfolio_id', 'portfolio_name',
                                                     'api_token', 'api_endpoint', 'environment', 'subscription_key'])


def store_credentials(creds: SwitchCredentials, key_prefix: str = ''):
    """
    Store credentials

    Parameters
    ----------
    creds
        SwitchCredentials to store
    key_prefix
        Key prefix to use when storage type is Env
        
    Returns
    -------
    None

    """

    key_prefix = key_prefix.upper()

    filename = _locate_creds_file(3)
    if not filename:
        filename = cred_filename

    creds_dict = _read_credentials_file(filename)

    creds_to_store = ''

    # Avoid duplicating entries with the same key prefix    
    if creds_dict:
        for key in creds_dict.copy().keys():
            if key.startswith(key_prefix):
                del creds_dict[key]

        # Ensure remaining keys are copied over
        for key in creds_dict.keys():
            creds_to_store += f"{key}={creds_dict[key]}\n"

    with open(filename, 'w') as file_in:
        creds_to_store += f"{key_prefix}_VERSION={creds.version}\n"
        creds_to_store += f"{key_prefix}_EMAIL={creds.email}\n"
        creds_to_store += f"{key_prefix}_USERID={creds.user_id}\n"
        creds_to_store += f"{key_prefix}_APITOKEN={creds.api_token}\n"
        creds_to_store += f"{key_prefix}_APIENDPOINT={creds.api_endpoint}\n"
        creds_to_store += f"{key_prefix}_ENVIRONMENT={creds.environment}\n"
        creds_to_store += f"{key_prefix}_SUBSCRIPTIONKEY={creds.subscription_key}\n"
        file_in.write(creds_to_store)


def read_credentials(key_prefix: str = '', portfolio_id: UUID = None, portfolio_name: str = ''):
    """Read Credentials

    Reads credentials from credential store

    Parameters
    ----------
    key_prefix
        Key prefix to use for the stored Keys
    portfolio_id
        Override output with given PortfolioId
    portfolio_name
        Override output with given PortfolioName

    Returns
    -------
    SwitchCredentials
        Returns the SwitchCredentials namedtuple containing credentials to call Switch APIs when found; otherwise False

    """
    key_prefix = key_prefix.upper()

    try:
        filepath = _locate_creds_file(num_dir_traversals=4)

        if filepath == False:
            return False

        creds_dict = _read_credentials_file(filepath)

        version_key = f"{key_prefix}_VERSION"
        version = creds_dict[version_key] if version_key in creds_dict else '0'

        creds = SwitchCredentials(
            version,
            creds_dict[f"{key_prefix}_EMAIL"],
            creds_dict[f"{key_prefix}_USERID"],
            portfolio_id,
            portfolio_name,
            creds_dict[f"{key_prefix}_APITOKEN"],
            creds_dict[f"{key_prefix}_APIENDPOINT"],
            creds_dict[f"{key_prefix}_ENVIRONMENT"],
            creds_dict[f"{key_prefix}_SUBSCRIPTIONKEY"]
        )

        return creds
    except Exception as e:
        print('Unable to read credentials file.', e)
        return False


def clear_credentials(key_prefix: str = ''):
    """Clear Credentials

    Clears credentials from credential store

    Parameters
    ----------
    storage_type
        Type of storage for the credentials
    key_prefix
        Key prefix to use when storage type is Env

    Returns
    -------
    None

    """
    key_prefix = key_prefix.upper()

    filename = _locate_creds_file(num_dir_traversals=4)

    store_credentials(SwitchCredentials('', '', '', '', '', '', '', '', ''), filename, key_prefix)


def _locate_creds_file(num_dir_traversals):
    """
    Credentials File search begins from the directory that the python script is executed from.
    Traversing back up dir tree could help us locate an existing creds file
    We will traverse given number of times. If file is still not found, user will need to login again.

    Limitations: Credentials file are created where a script is executed from.
                 This could result in multiple credentials file.
    Future: Investigate physical Credentials file alternatives.
    """

    try:
        # First try current directory 
        if path.isfile(cred_filename):
            return cred_filename

        # Then look at /switch directory. Only relevant during switch lib development.
        if path.isfile(f"switch/{cred_filename}"):
            return f"switch/{cred_filename}"

        # Then traverse down the directory tree given number of times
        # There may be times when authentication is run from a root directory
        # but script run from a subdirectory. This will help us find credentials file in the root dir.
        filepath = cred_filename
        for _ in range(num_dir_traversals):
            if path.isfile(filepath):
                # print(f"found credentials file under {path.abspath(filepath)}")
                return filepath
            else:
                # print(f"looked for credentials file under {path.abspath(filepath)}")
                filepath = f"../{filepath}"
    except:
        return False
    return False


def _read_credentials_file(filepath: str):
    if not path.isfile(filepath):
        return False

    with open(filepath, 'r') as file:
        file_content = file.read().splitlines()

    return dict(line.strip().split('=') for line in file_content)
