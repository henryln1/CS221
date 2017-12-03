# this runs inside the main of getData and thus has acess to the variables
# needs to have the cumulative ingedients list, the directions for each recipe, and a list of verbs used for cooking

import recipeUtil
import collections


def createCSP(listOfIngredients, allrecipeinstructions):
	num_ingredients = len(listOfIngredients)
	csp = recipeUtil.CSP()
  	
	with open('cooking_verbs.txt') as f:
		verbs = f.readlines()
	verbs = [x.strip() for x in verbs]

	verbDomain = [i for i in range(1, num_ingredients*2 + 1, 2)]
	verbDomain.append(0)
	ingredientDomain = [i for i in range(2, num_ingredients*2 + 1, 2)]

	# add variable for each verb in verb list
	for verb in verbs:
		csp.add_variable(verb, verbDomain)

 	# add variable for each ingredient in cumulative ingredients list
	for ingredient in listOfIngredients:
		csp.add_variable(ingredient, ingredientDomain)		
	
	# ensure each place in the order is assigned exactly one ingredient
	for ingredient in listOfIngredients:
		for ingredient2 in listOfIngredients:
			if ingredient != ingredient2:
				csp.add_binary_factor(ingredient, ingredient2, lambda x,y: x != y)
	
	# ensure no verbs are given the same assignment
	for verb in verbs:	
		for v in verbs: 				
			if v != verb:
				csp.add_binary_factor(verb, v, lambda x, y: x == 0 or x != y)

  	ingredientsSet = set(listOfIngredients)
	verbsSet = set(verbs)
	# qualifiers for our sentences
	thingsToAddTo = ["bowl", "skillet", "pot", "kettle", "saucepan", "pan", ""]
	csp.add_variable("add in", thingsToAddTo)
	csp.add_variable("heat in", thingsToAddTo)
	cookMinutes = [i for i in range(0, 61)]
	csp.add_variable("mins", cookMinutes)
	bowlSizes = ["small", "medium", "large", ""]
	csp.add_variable("bowl size", bowlSizes)
	addCounts = collections.defaultdict(int)
	heatCounts = collections.defaultdict(int)
	minuteCounts = collections.defaultdict(int)
	sizeCounts = collections.defaultdict(int)

	for recipe in allrecipeinstructions:
		prevIng = None
		prevVrb = None
		for sentence in recipe:
			sentence = sentence.lower()
			sentence = sentence.split(' ')
			sentenceSet = set(sentence)
			ingredientsInSentence = sentenceSet.intersection(ingredientsSet)
			verbsInSentence = sentenceSet.intersection(verbsSet)
		
			# weight ingredient immediately after verb
			def ingredientAndVerb(x, y):
				if x == y + 1:
					return 1.002
				else:
					return 1

			# generic function for ordering. used for ingredient ordering, verb ordering
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
					# find qualifiers to build sentences
					if vrb == "add" or vrb == "combine" or vrb == "mix" or vrb == "whisk" or vrb == "pour" or vrb == "stir":
						for noun in thingsToAddTo:
							addCounts[noun] += (noun in sentence)
					elif vrb == "heat":
						for noun in thingsToAddTo:
							heatCounts[noun] += (noun in sentence)
					elif vrb == "cook" or vrb == "boil" or vrb == "simmer" or vrb == "chill" or vrb == "refrigerate" or vrb == "bake":
						if "minutes" in sentence:
							numMinutes = sentence[sentence.index("minutes") - 1]
							if numMinutes.isdigit() and int(numMinutes) <= 60:
								minuteCounts[noun] += 1
					if vrb == "beat" or vrb == "add" or vrb == "combine" or vrb =="mix" or vrb =="whisk" or vrb =="pour":
						for size in bowlSizes:
							sizeCounts[noun] += (size in sentence)

	# count up frequency of sentence qualifiers
	for noun in addCounts:
		csp.add_unary_factor("add in", lambda x: 1 + (x == noun) * addCounts[noun] * .001)
		csp.add_unary_factor("heat in", lambda x: 1 + (x == noun) * heatCounts[noun] * .001)
	for num in minuteCounts:
		csp.add_unary_factor("mins", lambda x: 1 + (x == num) * minuteCounts[num] * .001)
	for size in sizeCounts:
		csp.add_unary_factor("bowl size", lambda x: 1 + (x == size) * sizeCounts[size] * .001)
						
	return csp		

def translateAssignment(numIngredients, assignment):
	reversedAssignment = dict((v,k) for k,v in assignment.iteritems())
	for i in range(1, numIngredients*2 + 1, 2):
		vrb = reversedAssignment[i]
		ing = reversedAssignment[i + 1]
		step = str(i/2 + 1) + ". " + vrb + " " + ing
		if vrb == "add" or vrb == "combine" or vrb == "mix" or vrb == "whisk" or vrb == "pour" or vrb == "stir":
			noun = assignment["add in"]
			if noun == "bowl" and assignment["bowl size"] != "":
				noun = assignment["bowl size"] + " " + noun
			inOrTo = " in " if vrb != "add" else " to "
			if noun != "":
				step += inOrTo + noun
		elif vrb == "heat":
			noun = assignment["heat in"]
			if noun != "":
				step += " in " + noun
		elif vrb == "cook" or vrb == "boil" or vrb == "simmer" or vrb == "chill" or vrb == "refrigerate" or vrb == "bake":
			mins = assignment["mins"]
			if mins != 0:
				step += " for " + str(mins) + " minutes"
		elif vrb == "beat":
			bowlSize = assignment["bowl size"]
			if bowlSize != "":
				step += " in " + bowlSize + " bowl"
		step += "."
		print step
				
def main(listOfIngredients, allrecipeinstructions):
	csp = createCSP(listOfIngredients, allrecipeinstructions)
	numIngredients = len(listOfIngredients)
	#search = recipeUtil.BacktrackingSearch()
	search = recipeUtil.BeamSearch()
	search.initialize(50)
	#search.reset_results()
	# toggle optimizations (ac3, etc) below
 	#print csp.binaryFactors
	# print csp.unaryFactors
	#search.solve(csp, len(listOfIngredients))
	search.solve(csp, len(listOfIngredients), True, True)
	assignments = [search.optimalAssignment]
	maxPrint = 20
	count = 0
	bestAssignment = []
	for assign in assignments:
		count += 1
		print "Raw Assignment:"
		assignment = {k: v for k, v in assign.items() if type(v) == str or v > 0}
		print assignment
		print "Translation:"
		translateAssignment(numIngredients, assignment)
		bestAssignment = assignment
		f1=open('testfile', 'w+')
		print >> f1, assignment
		f1.close()
		if count > maxPrint:
			break

	print recipeUtil.evaluationFunction(assignment, listOfIngredients, False)


