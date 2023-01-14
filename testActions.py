from __future__ import print_function

import glob

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time
months = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec"]

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1x2dVAd5YS8ifgIN9eV_kXcwRX7eXNQ1OfFiDmq5v6dg' #gym spreadsheet
# SPREADSHEET_ID = '13FkI3lmfiWU0oQt6uvEyXLAIw6s3RiWroA7fQOt98qI' #copy of gym spreadsheet

# Helper functions to create cells (otherwise it gets quite messy)
def createBorderedCell(val: str) -> dict:
    return dict(
        {
            'userEnteredValue':{
                'stringValue':val
            },
            'userEnteredFormat':{
                'borders':{
                    'top':{
                        'style':'SOLID',
                        'width':1,
                        'color':{
                            'red':0,
                            'green':0,
                            'blue':0,
                            'alpha':1,
                        }
                    },
                    'bottom':{
                        'style':'SOLID',
                        'width':1,
                        'color':{
                            'red':0,
                            'green':0,
                            'blue':0,
                            'alpha':1,
                        }
                    },
                    'left':{
                        'style':'SOLID',
                        'width':1,
                        'color':{
                            'red':0,
                            'green':0,
                            'blue':0,
                            'alpha':1,
                        }
                    },
                    'right':{
                        'style':'SOLID',
                        'width':1,
                        'color':{
                            'red':0,
                            'green':0,
                            'blue':0,
                            'alpha':1,
                        }
                    },
                },
                'horizontalAlignment':'CENTER'
            }
        }
    )

def createCell(val: str) -> dict:
    return dict(
        {
            'userEnteredValue':{
                'stringValue':val
            },
            'userEnteredFormat':{
                'horizontalAlignment':'CENTER'
            }
        }
    )


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    
    credFileName = glob.glob("gha-creds-*.json")[0]
    creds = service_account.Credentials.from_service_account_file(credFileName, scopes=SCOPES)

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        spreadsheet = service.spreadsheets()
        sheet_metadata = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        # Id of the previous week's sheet
        title = sheets[-1].get("properties", {}).get("title", 'fail')
        
        print(title)
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()