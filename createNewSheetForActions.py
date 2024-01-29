from __future__ import print_function

from google.oauth2 import service_account

import glob

months = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec"]

from createNewSheet import createNewSheet

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1_DNoLWQX8jXvogVROqdu6oQSneYQy5HdavRBskHO_Os' #gym spreadsheet 2
# SPREADSHEET_ID = '1x2dVAd5YS8ifgIN9eV_kXcwRX7eXNQ1OfFiDmq5v6dg' #gym spreadsheet 1
# SPREADSHEET_ID = '13FkI3lmfiWU0oQt6uvEyXLAIw6s3RiWroA7fQOt98qI' #copy of gym spreadsheet

# For starting new spreadsheet
OFFSET = 50

def main():
    
    credFileName = glob.glob("gha-creds-*.json")[0]
    creds = service_account.Credentials.from_service_account_file(credFileName, scopes=SCOPES)

    createNewSheet(creds)


if __name__ == '__main__':
    main()
    