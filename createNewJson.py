import json

test = [{"directions": ["1. Scoop the flour and sugar into a bowl", "2. Chop up onions and place them into the bowl.", "3. Pour milk into the bowl and mix"]}]


with open('testInstructions.json', 'w') as outfile:
	json.dump(test, outfile)

print 'success'
