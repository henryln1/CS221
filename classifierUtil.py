import random
import collections
import readData


def extractWordFeatures(x):
	words = x.split()
	features = collections.defaultdict(int)
	for i in range(len(words)):
		features[words[i]] += 1
	return features

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

def stochasticGradientDescent(features, weights, classification, stepsize):
	vector = gradientLossFunction(features, classification)

	for key in features:
		weights[key] = weights[key] - stepsize * vector[key]

	return weights	

def trainClassifier(recipes, classifications, stepsize):
	weights = collections.defaultdict(float)
	for i in range(len(recipes)):
		features = collections.defaultdict(float)

		currRecipe = recipes[i]
		currentClassification = classifications[i]
		#takes each line of instruction and extracts features from it
		for instruction in currRecipe:
			#extracts features that are tuples of words
			newFeatures = extractNGramFeatures(instruction, 4)
			for feat in newFeatures: #add them to the overall feature vector for this recipe
				features[feat] += newFeatures[feat]
		#by this point the feature vector for this current recipe is done, so we can run SGD on it
		weights = stochasticGradientDescent(features, weights, currentClassification, stepsize)
	print "weights ", weights	
	return weights
	

import stripRealRecipes

#randomly generates a dataset to try and train the classifier on
def generateEntireDataset(size, numIngredients):

	instructionsList = []
	classification = []

	numberFakeRecipes = random.randint(1, size)

	fakeRecipeList = readData.generateKFakeRecipes(numberFakeRecipes, numIngredients)

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
