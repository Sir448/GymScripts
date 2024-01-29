from __future__ import print_function

import glob

from google.oauth2 import service_account

from updateSheet import updateSheet

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def main():
    
    credFileName = glob.glob("gha-creds-*.json")[0]
    creds = service_account.Credentials.from_service_account_file(credFileName, scopes=SCOPES)

    updateSheet(creds)


if __name__ == '__main__':
    main()
    