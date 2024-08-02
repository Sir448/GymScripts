import json

with open('increments.json', 'r') as f:
    oldIncrements = json.load(f)

newIncrements = { name:{ 'increment': increment, 'maxReps': 10 } for name,increment in oldIncrements.items()}

# read current reps and weight

# increment
# maxreps
# currentreps
# currentweight
# alternate
# name