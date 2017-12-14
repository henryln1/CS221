# this runs inside the main of getData and thus has acess to the variables
# needs to have the cumulative ingedients list, the directions for each recipe, and a list of verbs used for cooking

import recipeUtil
import collections
import itertools


def createCSP(listOfIngredients, allrecipeinstructions, limit):
	num_ingredients = len(listOfIngredients)
	csp = recipeUtil.CSP()
  	
	with open('cooking_verbs.txt') as f:
		verbs = f.readlines()
	verbs = [x.strip() for x in verbs]

	verbDomain = [i for i in range(1, limit + 1)]
	verbDomain.append(0)
	for verb in verbs:
		csp.add_variable(verb, verbDomain)

 	# add variable for each ingredient in cumulative ingredients list
	for ingredient in listOfIngredients:	
		domain = []
		prevTuple = tuple()
		for i in range(limit, 0, -1):
			newTuple = prevTuple + (i,)
			domain.append(newTuple)
			prevTuple = newTuple
		csp.add_variable(ingredient, domain)

	
	# ensure no verbs are given the same assignment
	for verb in verbs:	
		for v in verbs: 				
			if v != verb:
				csp.add_binary_factor(verb, v, lambda x, y: x == 0  or x != y)

  	ingredientsSet = set(listOfIngredients)
	verbsSet = set(verbs)
	# qualifiers for our sentences
	thingsToAddTo = ["bowl", "skillet", "pot", "kettle", "saucepan", "pan", ""]
	thingsToHeatIn = ["skillet", "pot", "kettle", "saucepan", "pan", ""]
	csp.add_variable("add in", thingsToAddTo)
	csp.add_variable("heat in", thingsToHeatIn)
	bowlSizes = ["small", "medium", "large", ""]
	csp.add_variable("bowl size", bowlSizes)
	addCounts = collections.defaultdict(int)
	heatCounts = collections.defaultdict(int)
	sizeCounts = collections.defaultdict(int)

	for recipe in allrecipeinstructions:
		prevIng = None
		prevVrb = None
		firstVrb = None
		totalIngredients = set()
		totalVerbs = set()
		for sentence in recipe:
			sentence = sentence.lower()
			sentence = sentence.split(' ')
			sentenceSet = set(sentence)
			ingredientsInSentence = sentenceSet.intersection(ingredientsSet)
			verbsInSentence = sentenceSet.intersection(verbsSet)
		
			# weight ingredient immediately after verb
			def ingredientAndVerb(x, y):
				if y in x:
					return 1.002
				else:
					return 1

			# generic function for ordering. used for verb ordering
			def yAfterX(x, y):
				if y > x:
					return 1.006
				else:
					return 0.999

			def ingredientOrdering(x, y):
				factor = 1
				for indexX in x:
					for indexY in y:
						if indexY == 1 + indexX:
							factor *= 1.001
						if indexY < indexX:
							factor *= 0.999 # makes sure we don't just assign every ingredient to every verb
				if len(x) == len(y):
					factor *= 0.999
				return factor

			def verbBeforeIngredient(x, y):
				factor = 1
				for index in x:
					if index > y:
						factor *= 1.001
				return factor	

			for ing in ingredientsInSentence:
				# add binary factor to weight ingredient ordering
				if prevIng != None and prevIng != ing:
					csp.add_binary_factor(prevIng, ing, ingredientOrdering)
				prevIng = ing
				for vrb in verbsInSentence:
					# add binary factor here with function: if ingredient == verb + 1 then return a high number, else return a lower number
					csp.add_binary_factor(ing, vrb, ingredientAndVerb)				
					# add binary factor to weight for verb coming before ingredient		
					# if sentence.index(vrb) < sentence.index(ing):
					# 	csp.add_binary_factor(ing, vrb, verbBeforeIngredient)
					# add binary factor to weight verb ordering
					if firstVrb != None and firstVrb != vrb:
						csp.add_binary_factor(firstVrb, vrb, yAfterX)
					elif firstVrb == None:
						firstVrb = vrb
					if prevVrb != None and prevVrb != vrb:
						csp.add_binary_factor(prevVrb, vrb, yAfterX)
					# find qualifiers to build sentences
					if vrb == "add" or vrb == "combine" or vrb == "mix" or vrb == "whisk" or vrb == "pour" or vrb == "stir":
						for noun in thingsToAddTo:
							addCounts[noun] += (noun in sentence)
					elif vrb == "cook" or vrb == "boil" or vrb == "simmer" or vrb == "chill" or vrb == "refrigerate" or vrb == "bake" or vrb == "toast":
						for noun in thingsToHeatIn:
							heatCounts[noun] += (noun in sentence)
					if vrb == "beat" or vrb == "add" or vrb == "combine" or vrb =="mix" or vrb =="whisk" or vrb =="pour":
						for size in bowlSizes:
							sizeCounts[size] += (size in sentence)
			totalIngredients.update(ingredientsInSentence)
			totalVerbs.update(verbsInSentence)

		def weightValue(x):
			return 1.3
		if len(totalIngredients) >= num_ingredients - 2:
			for verb in totalVerbs:
				csp.add_unary_factor(verb, weightValue)

	# count up frequency of sentence qualifiers
	for noun in addCounts:
		csp.add_unary_factor("add in", lambda x: 1 + (x == noun) * addCounts[noun] * .001)
		csp.add_unary_factor("heat in", lambda x: 1 + (x == noun) * heatCounts[noun] * .001)
	for size in sizeCounts:
		csp.add_unary_factor("bowl size", lambda x: 1 + (x == size) * sizeCounts[size] * .001)

	return csp		

def translateAssignment(limit, assignment, returnStuff = False):
	returnList = []
	if not assignment:
		print "No recipe."
		return
	reversedIngs = collections.defaultdict(tuple)
	reversedVerbs = collections.defaultdict(int)
	for obj, indices in assignment.items():
		if type(indices) != tuple:
			reversedVerbs[indices] = obj
		else:
			for index in indices:
				reversedIngs[index] += (obj,)
	for i in range(1, limit + 1, 1):
		vrb = reversedVerbs[i]
		ings = reversedIngs[i]
		step = str(i) + ". " + str(vrb)
		first = True
		numIngs = len(ings)
		for j in range(0, numIngs):
			if j != 0 and numIngs != 2:
				step += ","
			if j == numIngs - 1 and numIngs != 1:
				step += " and"
			step += " " + ings[j]
		if vrb == "add" or vrb == "combine" or vrb == "mix" or vrb == "whisk" or vrb == "pour" or vrb == "stir":
			noun = assignment["add in"]
			if noun == "bowl" and assignment["bowl size"] != "":
				noun = assignment["bowl size"] + " " + noun
			inOrTo = " in " if vrb != "add" else " to "
			if noun != "":
				step += inOrTo + noun
		elif vrb == "cook" or vrb == "boil" or vrb == "simmer" or vrb == "chill" or vrb == "refrigerate" or vrb == "bake" or vrb == "toast" or vrb == "melt":
			noun = assignment["heat in"]
			if noun != "":
				step += " in " + noun
		elif vrb == "beat":
			bowlSize = assignment["bowl size"]
			if bowlSize != "":
				step += " in " + bowlSize + " bowl"
		step += "."
		if not returnStuff:
			print step
		else:
			returnList.append(step)
	if (returnStuff):
		return returnList
				
def main(listOfIngredients, allrecipeinstructions, returnAssignment = False):
	numIngredients = len(listOfIngredients)
	limit = numIngredients if numIngredients < 5 else 4
	csp = createCSP(listOfIngredients, allrecipeinstructions, limit)
	#search = recipeUtil.BacktrackingSearch()
	search = recipeUtil.BeamSearch()
	search.initialize(50)
	#search.reset_results()
	# toggle optimizations (ac3, etc) below
 	#print csp.binaryFactors
	# print csp.unaryFactors
	#search.solve(csp, len(listOfIngredients))
	search.solve(csp, limit, True, True)
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
		translateAssignment(limit, assignment)
		bestAssignment = assignment
		f1=open('testfile', 'w+')
		print >> f1, assignment
		f1.close()
		if count > maxPrint:
			break

	#k = recipeUtil.evaluationFunction(assignment, listOfIngredients, False)
	k = 1
	if (returnAssignment):
		return bestAssignment, k
	else:
		return k
