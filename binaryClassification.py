import random
import classifierUtil
import readData
import collections

def signNumber(x):

	if (x >= 0):
		return 1
	else:
		return -1

def binaryClassifier(K):

	fakeAndRealRecipes, classification = classifierUtil.generateEntireDataset(K)

	stepsize = 1.0/len(fakeAndRealRecipes)

	weights = classifierUtil.trainClassifier(fakeAndRealRecipes, classification, stepsize)


	#TODO: create testing datset to run this on

	fakeRecipes = readData.generateKFakeRecipes(30)

	ngram = 3
	correctCount = 0
	total = 0
	for recipe in fakeRecipes:
		features = collections.defaultdict(float)
		for instruction in recipe:
			#currFeatures = classifierUtil.extractNGramFeatures(instruction, 2)
			currFeatures = classifierUtil.extractWordFeatures(instruction)
			for key in currFeatures:
				features[key] += currFeatures[key]

		value = classifierUtil.dotProduct(features, weights)
		print value
		if (signNumber(value) == -1):
			correctCount += 1
		total += 1

		print "Percentage Correct: ", float(correctCount)/total

binaryClassifier(100)
