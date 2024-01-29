import json

def increment(values, update=False):
    new = {}

    # Load increment values

    with open("increments.json", 'r') as f:
        increments = json.load(f)

    # Set new reps and weights in dictionary

    for row in (values if update else values[::-1]):
        if len(row) == 0: continue

        exerciseName = row[0].strip().title()
        
        if exerciseName in new or exerciseName == 'Max Incline Walk': continue
        
        reps = int(row[2])
        weight = float(row[3])
        goNext = len(row) > 5
        
        if goNext and reps == 8:
            new[exerciseName] = ("12", row[3])
        elif goNext:
            newWeight = weight + increments.get(exerciseName,5)
            if newWeight%1 == 0:
                newWeight = int(newWeight)
            new[exerciseName] = ("8", str(newWeight))
        else:
            new[exerciseName] = (str(reps), row[3])

    return new