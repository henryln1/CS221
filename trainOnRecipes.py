# this runs inside the main of getData and thus has acess to the variables
# needs to have the cumulative ingedients list, the directions for each recipe, and a list of verbs used for cooking

import recipeUtil


#me playing around, don't pay much attention. 
def createCSPTest(listOfIngredients, allrecipeinstructions):
	num_ingredients = len(listOfIngredients)
	csp = recipeUtil.CSP()
  	
	with open('cooking_verbs.txt') as f:
		verbs = f.readlines()
	verbs = [x.strip() for x in verbs]
	
	#add an empty domain for each verb variable that we will update later
	
	domain = [0]
	for verbs in verbs:
		csp.add_variable(verb, domain)
	
	# add variable for each ingredient in cumulative ingredients list
	for ingredient in listOfIngredients:
		csp.add_variable(ingredient, [i for i in range(1, num_ingredients*2 + 1)])
		
		# ensure ingredients are always assigned after verbs (aka ingredients given even assignmnets)
		csp.add_unary_factor(ingredient, lambda x: x % 2 == 0)
		
		#TODO: need to add a piece that makes sure each verb or ingredient has a unique assignment
	
	pass
	

def createCSP(listOfIngredients, allrecipeinstructions):
	num_ingredients = len(listOfIngredients)
	csp = recipeUtil.CSP()
  	
	with open('cooking_verbs.txt') as f:
		verbs = f.readlines()
	verbs = [x.strip() for x in verbs]


	# add variable for each verb	
	domain = [0]
	for verb in verbs:
    		#csp.add_variable(verb, [i for i in range(0, num_ingredients*2 + 1)])
		csp.add_variable(verb, domain)
		# ensure verb always assigned before ingredient (aka verbs given odd assignments
		#csp.add_unary_factor(verb, lambda x: x == 0 or x % 2 != 0)

	#Currently we only about the verb variables that appear in the same sentence as an ingredient. Otherwise,
	# we don't add it to the CSP at all and ignore it completely. 
	ingredientsSet = set(listOfIngredients)
	verbsSet = set(verbs)
	relevantVerbs = set()
	for recipe in allrecipeinstructions:
		for sentence in recipe:
			sentence = sentence.lower()
			sentence = sentence.split(' ')
			sentenceSet = set(sentence)
			ingredientsInSentence = sentenceSet.intersection(ingredientsSet)
			verbsInSentence = sentenceSet.intersection(verbsSet)
			relevantVerbs.update(verbsInSentence)
			for ing in ingredientsInSentence:
				for ver in verbsInSentence:
					d = [i for i in range(0, num_ingredients*2 + 1) if i%2 != 0]
					d.append(0)
					csp.add_variable(ver, d)
					#csp.add_unary_factor(ver, lambda x: x == 0 or x % 2 != 0)

	
 # add variable for each ingredient in cumulative ingredients list
	for ingredient in listOfIngredients:
		csp.add_variable(ingredient, [i for i in range(1, num_ingredients*2 + 1)])
		
		# ensure ingredients are always assigned after verbs (aka ingredients given even assignmnets)
		csp.add_unary_factor(ingredient, lambda x: x % 2 == 0)
		
		# ensure only one verb/ingredient is assigned a number 
		for verb in verbs:
			csp.add_binary_factor(ingredient, verb, lambda x,y: x != y)		
	
	# ensure each place in the order is assigned exactly one ingredient
	for ingredient in listOfIngredients:
		for ingredient2 in listOfIngredients:
			if ingredient != ingredient2:
				csp.add_binary_factor(ingredient, ingredient2, lambda x,y: x != y)
	
	# ensure no verbs are given the same assignment
	for verb in verbs:	
			for v in verbs: 				
				if v != verb:
					csp.add_binary_factor(verb, v, lambda x, y: x == 0  or x != y)

	# lol i dont know how to do a for loop that increments by 2
	# ensures that all the order has verbs assigned for every position (aka not all verbs are zero)
	i = 1
	while i < num_ingredients * 2:
		var = recipeUtil.get_or_variable(csp, 'slot' + str(i), verbs, i)
		csp.add_unary_factor(var, lambda x: x)
		i+= 2
	
	#return csp


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

 #TODO:
  #add a factor that when 2 ingredients appear in the same sentence, weight them accordingly based on which came first
  	
	for recipe in allrecipeinstructions:
		prevIng = None
		prevVrb = None
		for sentence in recipe:
			sentence = sentence.lower()
			sentence = sentence.split(' ')
			sentenceSet = set(sentence)
			ingredientsInSentence = sentenceSet.intersection(ingredientsSet)
			verbsInSentence = sentenceSet.intersection(verbsSet)
		
			def ingredientAndVerb(x, y):
				if x == y + 1:
					return 1.002
				else:
					return 1

			# generic function for ordering. used for verb before ingredient, ingredient ordering, verb ordering
			def yAfterX(x, y):
				if y > x:
					return 1.001
				else:
					#returning 1 to indicate no weight
					return 1

			for ing in ingredientsInSentence:
				# add binary factor to weight ingredient ordering
				if prevIng != None and prevIng != ing:
					csp.add_binary_factor(prevIng, ing, yAfterX)
				prevIng = ing
				for vrb in verbsInSentence:
					# add binary factor here with function: if ingredient == verb + 1 then return a high number, else return a lower number
					csp.add_binary_factor(ing, vrb, ingredientAndVerb)				
					# add binary factor to weight for verb coming before ingredient		
					if sentence.index(vrb) > sentence.index(ing):
						csp.add_binary_factor(ing, vrb, yAfterX)
					# add binary factor to weight verb ordering
					if prevVrb != None and prevVrb != vrb:
						csp.add_binary_factor(prevVrb, vrb, yAfterX)
					prevVrb = vrb

						
	return csp		
				
def main(listOfIngredients, allrecipeinstructions):
	csp = createCSP(listOfIngredients, allrecipeinstructions)
	search = recipeUtil.BacktrackingSearch()
	# toggle optimizations (ac3, etc) below
 	#print csp.binaryFactors
	# print csp.unaryFactors
	search.solve(csp)
	assignments = [search.optimalAssignment]
	maxPrint = 20
	count = 0
	for assign in assignments:
		count += 1
		assignment = {k: v for k, v in assign.items() if v > 0 and v <= len(listOfIngredients) * 2 and k[0] != 'or'}
		print assignment
		if count > maxPrint:
			break
			
			
