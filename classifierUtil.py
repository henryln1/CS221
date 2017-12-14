import random
import collections
import readData


def extractWordFeatures(x):
	"""
	Extract word features for a string x. Words are delimited by
	whitespace characters only.
	@param string x: 
	@return dict: feature vector representation of x.
	Example: "I am what I am" --> {'I': 2, 'am': 2, 'what': 1}
	"""
	# BEGIN_YOUR_CODE (our solution is 4 lines of code, but don't worry if you deviate from this)
	#raise Exception("Not implemented yet")
	words = x.split()
	features = collections.defaultdict(int)
	for i in range(len(words)):
		features[words[i]] += 1
	return features
	# END_YOUR_CODE

def extractNGramFeatures(x, n):

	#features are tuples of words, where x is the number of words in each tuple
	#returns dict of feature vector
	words = x.split()
	print words
	features = collections.defaultdict(float)

	for i in range(len(words)):
		currentTupleList = []
		for j in range(i, i + n):
			if (j < len(words)):
				currentTupleList.append(words[j])
		tupleForm = tuple(currentTupleList)
		features[tupleForm] += 1
	print features
	return features

def dotProduct(features, weights):
	total = 0

	for key in features:
		total += features[key] * weights[key]

	return total

#hinge loss function
def gradientLossFunction(features, classification):
	returnVector = collections.defaultdict(float)

	for key in features:

		returnVector[key] = (-1) * features[key] * classification

	return returnVector
	#pass

def stochasticGradientDescent(features, weights, classification, stepsize):

	vector = gradientLossFunction(features, classification)

	for key in weights:

		weights[key] = weights[key] - stepsize * vector[key]

	return weights	

def trainClassifier(recipes, classifications, stepsize):

	#TODO, decide what kind of classifer and actually write our classification function
	weights = collections.defaultdict(float)
	for i in range(len(recipes)):
		features = collections.defaultdict(float)

		currRecipe = recipes[i]
		currentClassification = classifications[i]
		#takes each line of instruction and extracts features from it
		for instruction in currRecipe:
			
			#extracts features that are tuples of words
			#newFeatures = extractNGramFeatures(instruction, 2)
			newFeatures = extractWordFeatures(instruction)
			for feat in newFeatures: #add them to the overall feature vector for this recipe
				features[feat] += newFeatures[feat]
		#by this point the feature vector for this current recipe is done, so we can run SGD on it
		weights = stochasticGradientDescent(features, weights, currentClassification, stepsize)
	print "weights ", weights


				
	return weights
	

import stripRealRecipes

#randomly generates a dataset to try and train the classifier on
def generateEntireDataset(size):

	instructionsList = []
	classification = []

	numberFakeRecipes = random.randint(1, size)

	fakeRecipeList = readData.generateKFakeRecipes(numberFakeRecipes)

	for  i in range(len(fakeRecipeList)):
		instructionsList.append(fakeRecipeList[i])
		classification.append(-1)

	#now we need to add a bunch of real recipes

	realRecipes = stripRealRecipes.getStrippedRealRecipes()

	realRecipesSample = random.sample(realRecipes, size-  len(fakeRecipeList))

	for i in range(len(realRecipesSample)):
		instructionsList.append(realRecipesSample[i])
		classification.append(1)

	return instructionsList, classification