from __future__ import print_function

import glob
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from createCells import createBorderedCell

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.

SPREADSHEET_ID = '1_DNoLWQX8jXvogVROqdu6oQSneYQy5HdavRBskHO_Os' #gym spreadsheet 2
# SPREADSHEET_ID = '1x2dVAd5YS8ifgIN9eV_kXcwRX7eXNQ1OfFiDmq5v6dg' #gym spreadsheet 1
# SPREADSHEET_ID = '13FkI3lmfiWU0oQt6uvEyXLAIw6s3RiWroA7fQOt98qI' #copy of gym spreadsheet

def main():
    
    credFileName = glob.glob("gha-creds-*.json")[0]
    creds = service_account.Credentials.from_service_account_file(credFileName, scopes=SCOPES)
    
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        spreadsheet = service.spreadsheets()
        sheet_metadata = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        
        # Title and id of the current sheet
        title = sheets[-1].get("properties", {}).get("title", "")
        sheet_id = sheets[-1].get("properties", {}).get("sheetId", 0)
        
        # Reading the values of the current sheet (to see what to increment)
        
        dataRange = title + '!D2:I33'
        
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=dataRange).execute()
        values = result.get('values', [])
        
        new = {}
        
        # Load increment values
        
        with open("increments.json", 'r') as f:
            increments = json.load(f)
        
        # Set new reps and weights in dictionary
        
        for row in values:
            if len(row) == 0: continue
            
            exerciseName = row[0].strip()
            
            if exerciseName in new or exerciseName == 'Max Incline walk': continue
            
            reps = int(row[2])
            weight = float(row[3])
            goNext = len(row) > 5
            
            if goNext and reps == 8:
                new[exerciseName] = ("12", row[3])
            elif goNext:
                newWeight = weight + increments[exerciseName]
                if newWeight%1 == 0:
                    newWeight = int(newWeight)
                new[exerciseName] = ("8", str(newWeight))
            else:
                new[exerciseName] = (str(reps), row[3])
                
        # Incrementing the values
        
        body = {
            'requests': [
                {
                    'updateCells':{
                        'rows':[
                        ],
                        'fields':'*',
                        'start':{
                            'sheet_id':sheet_id,
                            'rowIndex': 1,
                            'columnIndex': 5
                        }
                    },
                },
            ]
        }
        
        seenExercises = set()
        
        for row in values:
            if len(row) > 0 and row[0].strip() != 'Max Incline walk':
                exerciseName = row[0].strip()
                if exerciseName in seenExercises:
                    body['requests'][0]['updateCells']['rows'].append(
                        {
                            'values':[
                                createBorderedCell(new[exerciseName][0]),
                                createBorderedCell(new[exerciseName][1]),
                            ]
                        }
                    )
                else:
                    body['requests'][0]['updateCells']['rows'].append({})
                    seenExercises.add(exerciseName)
            else:
                body['requests'][0]['updateCells']['rows'].append({})
                
        request = spreadsheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body)
        response = request.execute()
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()
    