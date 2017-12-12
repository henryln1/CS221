#returns list of recipes cut down to the same format as our csp generates

from readData import *

def getStrippedRealRecipes():
	allRecipes = readInstructions("full_format_recipes.json")
	
	thingsToKeep = set()

	file = open('allIngredients.txt', 'r')
	allIngredients = file.readlines()
	file.close()

	allIngredients = [x.strip() for x in allIngredients]

	with open('cooking_verbs.txt') as f:
		verbs = f.readlines()
	verbs = [x.strip() for x in verbs]

	thingsToKeep.update(allIngredients)
	thingsToKeep.update(verbs)

	thingsToKeep.update(['bowl', 'in', 'on', 'to', 'for', 'minutes', 'and'])
	thingsToKeep.update(["bowl", "skillet", "pot", "kettle", "saucepan", "pan"])
	thingsToKeep.update(["small", "medium", "large"])
	thingsToKeep.update([str(i) for i in range(0, 61)])

	strippedRecipes = []

	for recipe in allRecipes:
		newRecipe = []
		hasIngredients = False
		for instruction in recipe:
			words = instruction.split(' ')
			newInstruction = []
			for word in words:
				if word in allIngredients:
					hasIngredients = True
				word = word.strip('.')
				word = word.strip(',')
				if word in thingsToKeep:
					newInstruction.append(word)
			newRecipe.append(' '.join(newInstruction))
		if hasIngredients:
			strippedRecipes.append(newRecipe)

	return strippedRecipes


print getStrippedRealRecipes()




