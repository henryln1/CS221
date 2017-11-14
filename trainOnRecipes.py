# this runs inside the main of getData and thus has acess to the variables
# needs to have the cumulative ingedients list, the directions for each recipe, and a list of verbs used for cooking

import recipeUtil.py



def createCSP():
	max_ingredients = 10
	csp = recipeUtil.CSP()
  # add variable for each verb
	with open('cooking_verbs.txt') as f:
		verbs = f.readLines()
	verbs = [x.strip() for x in verbs]
  	for verb in verbs:
    		csp.add_variable(verb, [i for i in range(0, max_ingredients + 1)])
	
 # add variable for each ingredient in cumulative ingredients list
	for ingredient in listOfIngredients:
		csp.add_variable(verb, [i for i in range(0, max_ingredients + 1)])


  # iterate over each sentence in directions 
  # - identify ingredients in sentence
  # - identify verbs in sentence
  # - add binary factor for each ingredient in each sentence and verbs in sentence
  # - add binary factor for order of verbs in sentence
  # - add binary factor for order of verbs from previous sentence to this sentence
  # (ie weight assignment of verb from sentence 1 higher if the assignment of verb 1 < assignment of verb 2)
  # add factors to constrain only one verb to each assignment 1-10 and only one ingredient to each assignment 1-10
  	ingredientsSet = set(listOfIngredients)
	verbsSet = set(verbs)
	previousSentenceVerbs = []
	for instructions in allinstructions:
		for sentence in instructions:
			sentence = set(sentence)
			ingredientsInSentence = sentence.intersection(ingredientsSet)
			verbsInSentence = sentence.intersection(verbsSet)
			# add binary factor here with function: if ingredient == verb then return a high number, else return a lower number
			# how to determine this number?? maybe start with arbitrary hihg and low numbers and then later figure out how to 
			# set the weight to the number of times these two have occurred together
			
  
  
  
