# this runs inside the main of getData and thus has acess to the variables
# needs to have the cumulative ingedients list, the directions for each recipe, and a list of verbs used for cooking

import recipeUtil

def createCSP(listOfIngredients, allrecipeinstructions):
<<<<<<< HEAD
	num_ingredients = len(listOfIngredients)
=======
	max_ingredients = len(listOfIngredients):
>>>>>>> 59af60bfe4ed325b57650f494db4d88834e9543e
	csp = recipeUtil.CSP()
  	
	with open('testVerbs.txt') as f:
		verbs = f.readlines()
	verbs = [x.strip() for x in verbs]


# add variable for each verb	
	for verb in verbs:
    		csp.add_variable(verb, [i for i in range(0, num_ingredients*2 + 1)])
		
		# ensure verb always assigned before ingredient (aka verbs given odd assignments
		csp.add_unary_factor(verb, lambda x: x == 0 or x % 2 != 0)
	
	
	
 # add variable for each ingredient in cumulative ingredients list
	for ingredient in listOfIngredients:
		csp.add_variable(ingredient, [i for i in range(1, num_ingredients*2 + 1)])
		
		# ensure ingredients are always assigned after verbs (aka ingredients given even assignmnets)
		csp.add_unary_factor(ingredient, lambda x: x % 2 == 0)
		
		# ensure only one verb/ingredient is assigned a number 
		for verb in verbs:
			csp.add_binary_factor(ingredient, verb, lambda x,y: x == 0 or y == 0 or x != y)		
	
	# ensure each place in the order is assigned exactly one ingredient
	for ingredient in listOfIngredients:
		for ingredient2 in listOfIngredients:
			if ingredient != ingredient2:
				csp.add_binary_factor(ingredient, ingredient2, lambda x,y: x != y)
	
	# ensure no verbs are given the same assignment
	for verb in verbs:	
			for v in verbs: 				
				if v != verb:
					csp.add_binary_factor(verb, v, lambda x, y: x != y)

	

	#CODE BELOW TAKES A LONG ASS TIME
	# #ensure each number in order is assigned an ingredient or verb
	# for i in range(1, num_ingredients + 1):
	# 	var = recipeUtil.get_or_variable(csp, 'or', csp.variables, i)
	# 	csp.add_unary_factor(var, lambda x: x)


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
<<<<<<< HEAD
			sentence = sentence.lower()
			sentence = sentence.split(' ')
			sentenceSet = set(sentence)
			ingredientsInSentence = sentenceSet.intersection(ingredientsSet)
			verbsInSentence = sentenceSet.intersection(verbsSet)

			# print sentence
			# print ingredientsSet
			# print ingredientsInSentence
			# print '--------------------'
			# print verbsSet
			# print verbsInSentence
			# print '*********************'
			
			
=======
			sentence = set(sentence)
			ingredientsInSentence = sentence.intersection(ingredientsSet)
			verbsInSentence = sentence.intersection(verbsSet)
			# add binary factor here with function: if ingredient == verb then return a high number, else return a lower number
>>>>>>> 59af60bfe4ed325b57650f494db4d88834e9543e
			def ingredientAndVerb(x, y):
				if x == y + 1:
					return 2
				else:
					return 1
			def verbBeforeIngredient(x, y):
				if y > x:
					return 2
				else:
					#returning 1 to indicate no weight
					return 1

			for ing in ingredientsInSentence:
				for vrb in verbsInSentence:
					# add binary factor here with function: if ingredient == verb + 1 then return a high number, else return a lower number
					csp.add_binary_factor(ing, vrb, ingredientAndVerb)				
					# add binary factor to weight for verb coming before ingredient		
					if sentence.index(vrb) > sentence.index(ing):
						csp.add_binary_factor(ing, vrb, verbBeforeIngredient)
						
	return csp		
				
def main(listOfIngredients, allrecipeinstructions):
	csp = createCSP(listOfIngredients, allrecipeinstructions)
	search = recipeUtil.BacktrackingSearch()
	# toggle optimizations (ac3, etc) below
 	#print csp.binaryFactors
	# print csp.unaryFactors
	search.solve(csp)
	assignment = search.optimalAssignment
	print assignment
			
  
  
  
