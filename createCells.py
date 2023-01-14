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
