# this runs inside the main of getData and thus has acess to the variables
# needs to have the cumulative ingedients list, the directions for each recipe, and a list of verbs used for cooking

import recipeUtil.py

def createCSP(listOfIngredients, allrecipeinstructions):
	max_ingredients = len(listOfIngredients):
	csp = recipeUtil.CSP()
  	
	with open('cooking_verbs.txt') as f:
		verbs = f.readLines()
	verbs = [x.strip() for x in verbs]

# add variable for each verb	
	for verb in verbs:
    		csp.add_variable(verb, [i for i in range(0, max_ingredients*2 + 1)])
		
		# ensure verb always assigned before ingredient (aka verbs given odd assignments
		csp.add_unary_factor(verb, lambda x: x == 0 or x % 2 != 0)
		
		for v in verbs: 
			# ensure no verbs are given the same assignment
			if v != verb:
				csp.add_binary_factor(verb, v, lambda x, y: x != y)
	
 # add variable for each ingredient in cumulative ingredients list
	for ingredient in listOfIngredients:
		csp.add_variable(ingredient, [i for i in range(0, max_ingredients + 1)])
		
		# ensure ingredients are always assigned after verbs (aka ingredients given even assignmnets)
		csp.add_unary_factor(ingredient, lambda x: x != 0 or x % 2 == 0)
		
		for verb in verbs:
			# ensure only one verb/ingredient is assigned a number 
			csp.add_binary_factor(ingredient, verb, lambda x,y: x == 0 or y == 0 or x != y)		
		
		for ingredient2 in listOfIngredients:
			# ensure each place in the order is assigned exactly one ingredient
			if ingredient != ingredient2:
				csp.add_binary_factor(ingredient, ingredient2, lambda x,y: x != y)



#DONE (below) :
  # iterate over each sentence in directions 
  # - identify ingredients in sentence
  # - identify verbs in sentence
  # - add binary factor for each ingredient in each sentence and verbs in sentence
  # - add binary factor for when a verb comes before an ingredient - not optimal 
#TO DO:
  # - add binary factor for order of verbs from previous sentence to this sentence -
  # - add binary factor for order of ingredients 
  # (ie weight assignment of verb from sentence 1 higher if the assignment of verb 1 < assignment of verb 2)
  # add factors to constrain only one verb and ingredient to each assignment 1-20 (should go verb, ingredient, verb, ingredient etc.)
# add factor weighting based on recipe rating??


#THINGS TO CONSIDER:
# - this framework will only allow one verb per ingredient (no repeating verbs)
  	
	ingredientsSet = set(listOfIngredients)
	verbsSet = set(verbs)
	for recipe in allrecipeinstructions:
		for sentence in recipe:
			sentence = set(sentence)
			ingredientsInSentence = sentence.intersection(ingredientsSet)
			verbsInSentence = sentence.intersection(verbsSet)
			# add binary factor here with function: if ingredient == verb then return a high number, else return a lower number
			def ingredientAndVerb(x, y):
				if x == y and x != 0:
					return 2
				else:
					return 1
			for ing in ingredientsSet:
				for vrb in verbsInSentence:
					csp.add_binary_factor(ing, vrb, ingredientAndVerb)
					def verbBeforeIngredient(x, y):
						if x > y:
							return 2
						else:
							#returning 1 to indicate no weight
							return 1
					if sentence.indexOf(vrb) > sentence.indexOf(ing):
						csp.add_binary_factor(ing, vrb, verbBeforeIngredient)
						
	return csp		
				
def main():
	csp = createCSP()
	search = recipeUtil.BacktrackingSearch()
	# toggle optimizations (ac3, etc) below
	search.solve(csp)
	assignment = search.optimalAssignment
	print assignment
			
  
  
  
