import os
import pickle
from typing import Tuple

import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from nure.sync.cache import LocalFileCache


class GoogleSheet(LocalFileCache):
    def __init__(self, key_file, credential_file, root_path='data/googlesheet', ttl=None) -> None:
        super().__init__(root_path, ttl=ttl)
        self.key_file = key_file
        self.credential_file = credential_file

    def _parse_key_(key: dict) -> Tuple[str, str]:
        if not isinstance(key, dict):
            raise TypeError('key must be a dict')

        spreadsheet_id = key['spreadsheet_id']
        range_ = key['range']
        return spreadsheet_id, range_

    def key_to_local_relative_path(self, key, *args, **kargs) -> str:
        spreadsheet_id, range_ = GoogleSheet._parse_key_(key)
        components = range_.split('!')
        if len(components) == 1:
            # sheet_name or cell range
            if len(components[0].split(':')) == 2:
                sheet_name = None
            else:
                sheet_name = components[0]
        else:
            sheet_name = '!'.join(components[:-1])

        if sheet_name is None:
            return f'{spreadsheet_id}.csv'

        if sheet_name.startswith("'") and sheet_name.endswith("'"):
            sheet_name = sheet_name[1:-1]

        relative_path = os.path.join(spreadsheet_id, f'{sheet_name}.csv')
        return relative_path

    def retrieve(self, key, local_file_path, header=False, *args, **kargs) -> None:
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        spreadsheet_id, range_ = GoogleSheet._parse_key_(key)
        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credential_file, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.key_file, 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_).execute()

        values = result['values']

        columns = header
        if header is True:
            columns = values[0]
            values = values[1:]

        pd_data = pd.DataFrame(data=result['values'], columns=columns)
        pd_data.to_csv(local_file_path, index=False)
