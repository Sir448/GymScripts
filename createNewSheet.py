from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time
months = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sept","Oct","Nov","Dec"]

from createCells import createBorderedCell, createCell
from increment import increment

import json

# The ID and and offset to start new sheet
with open("sheet.json") as f:
    data = json.load(f)
    SPREADSHEET_ID = data['sheetId']
    OFFSET = data ['offset']

def createNewSheet(creds):
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        spreadsheet = service.spreadsheets()
        sheet_metadata = spreadsheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        # Id of the previous week's sheet
        sheet_id = sheets[-1].get("properties", {}).get("sheetId", 0)
        
        
        # Creating the new blanksheet
        
        today = time.localtime()
        # Name of the new sheet
        name = f'week {OFFSET + len(sheets) + 1} - {months[today.tm_mon-1]} {today.tm_mday}, {today.tm_year}'
        
        body = {
            'requests': [
                {
                    'addSheet':{
                        'properties': {
                            'title': name
                        },
                        
                    },
                }
            ]
        }
        
        request = spreadsheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body)
        response = request.execute()
        new_sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
        
        # Copying previous sheet and resizing columns
        
        body = {
            'requests': [
                {
                    'copyPaste':{
                        'source':{
                            'sheet_id':sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 37,
                            'startColumnIndex': 0,
                            'endColumnIndex': 9,
                        },
                        'destination':{
                            'sheet_id':new_sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 37,
                            'startColumnIndex': 0,
                            'endColumnIndex': 9,
                        }
                        
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                        "sheetId": new_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 7,
                        "endIndex": 8
                        },
                        "properties": {
                        "pixelSize": 816
                        },
                        "fields": "pixelSize"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                        "sheetId": new_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 3,
                        "endIndex": 4
                        },
                        "properties": {
                        "pixelSize": 164
                        },
                        "fields": "pixelSize"
                    }
                },
            ]
        }
        
        request = spreadsheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body)
        response = request.execute()
        
        
        # Reading the values of the old sheet (to see what to increment)
        
        dataRange = name + '!D2:I37'
        
        
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=dataRange).execute()
        values = result.get('values', [])
        
        new = increment(values)
                
        # Updating sheet
        
        body = {
            'requests': [
                {
                    'updateCells':{
                        'rows':[
                        ],
                        'fields':'*',
                        'start':{
                            'sheet_id':new_sheet_id,
                            'rowIndex': 1,
                            'columnIndex': 5
                        }
                    },
                },
            ]
        }
        
        for i,row in enumerate(values):
            if len(row) > 0 and row[0].strip() != 'Max Incline walk':
                exerciseName = row[0].strip().title()
                alternate = None
                if len(new[exerciseName]) == 3:
                    alternate = new[exerciseName][2]
                reps, weight = new[alternate if alternate else exerciseName]
                body['requests'][0]['updateCells']['rows'].append(
                    {
                        'values':[
                            createBorderedCell(reps),
                            createBorderedCell(weight),
                            createCell(''),
                            createCell(''),
                        ]
                    }
                )

                # For alternating between exercises between weeks
                if alternate:
                    body['requests'].append(
                        {
                            'updateCells':{
                                'rows':[
                                    {
                                        'values':[
                                            createBorderedCell(alternate),
                                        ]
                                    }
                                ],
                                'fields':'*',
                                'start':{
                                    'sheet_id':new_sheet_id,
                                    'rowIndex': 1+i,
                                    'columnIndex': 3
                                }
                            },
                        }
                    )

            else:
                body['requests'][0]['updateCells']['rows'].append({})
                
                
        request = spreadsheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body)
        response = request.execute()
    except HttpError as err:
        print(err)
    