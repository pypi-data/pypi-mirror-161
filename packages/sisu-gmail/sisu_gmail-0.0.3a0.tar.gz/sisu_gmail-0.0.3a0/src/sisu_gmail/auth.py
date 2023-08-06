import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def start_auth_flow(app_creds_path, token_path, scopes):
    """Start Google auth flow using app_creds at path_to_app_creds

    :param app_creds_path: path_to_app_creds to app_creds.json file
    :param token_path: path_to_app_creds to store resulting auth app_creds
    :param scopes: Gmail API permission scope to request
    :return: token_path to the app_creds
    """
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(
            token_path,
            scopes
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(app_creds_path, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    return token_path


def authorize_resource(credentials):
    """Create an authorized Gmail API resource

    :param credentials: google.oauth2.app_creds.Credentials
    :return: googleapiclient.discovery.Resource
    """
    return build('gmail', 'v1', credentials=credentials)


def creds_from_json(token_json):
    """Create google.oauth2.app_creds from token_json

    :param token_json: dict: Gmail API user_token json loaded as dict
    :return: google.oauth2.app_creds.Credentials
    """
    return Credentials.from_authorized_user_info(token_json)


def refresh_token(credentials):
    """Call api with an empty Request to refresh token_path

    :param credentials: google.oauth2.credentials.Credentials
    :return: credentials: google.oauth2.credentials.Credentials
    """
    credentials.refresh(Request())
    return credentials
