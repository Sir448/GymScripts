import json

INCREMENTS_FILE = "increments.json"

def increment(values, update=False):
    new = {}

    # Load increment values

    with open(INCREMENTS_FILE, 'r') as f:
        increments = json.load(f)

    # Set new reps and weights in dictionary

    for row in (values if update else values[::-1]):
        if len(row) == 0: continue

        exerciseName = row[0].strip().title()
        
        if exerciseName in new or exerciseName == 'Max Incline Walk': continue
        
        reps = int(row[2])
        weight = float(row[3])
        goNext = len(row) > 5
        
        if goNext and reps < increments.get(exerciseName,{"maxReps":10})["maxReps"]:
            new[exerciseName] = (str(reps+2), row[3])
            increments[exerciseName]["currentReps"] += 2
        elif goNext:
            newWeight = weight + increments.get(exerciseName,{"increment":5})["increment"]
            if newWeight%1 == 0:
                newWeight = int(newWeight)
            new[exerciseName] = ("8", str(newWeight))
            increments[exerciseName]["currentReps"] = 8
            increments[exerciseName]["currentWeight"] = newWeight
        else:
            new[exerciseName] = (str(reps), row[3])

        if "alternate" in increments.get(exerciseName,{}):
            alternate = increments[exerciseName]["alternate"]
            new[exerciseName] = (new[exerciseName][0], new[exerciseName][1], alternate)
            new[alternate] = (str(increments[alternate]["currentReps"]),str(increments[alternate]["currentWeight"]))

    with open(INCREMENTS_FILE, 'w') as f:
        json.dump(increments, f, indent=4)

    return new