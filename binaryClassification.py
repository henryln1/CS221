import random
import classifierUtil
import readData
import collections

def signNumber(x):

	if (x >= 0):
		return 1
	else:
		return -1

def binaryClassifier(K, N = 0):

	fakeAndRealRecipes, classification = classifierUtil.generateEntireDataset(K, 0)

	stepsize = 1.0/len(fakeAndRealRecipes)

	weights = classifierUtil.trainClassifier(fakeAndRealRecipes, classification, stepsize)

	for i in range(11):
		fakeRecipes = readData.generateKFakeRecipes(30, i)

		ngram = 3
		correctCount = 0
		total = 0
		for recipe in fakeRecipes:
			features = collections.defaultdict(float)
			for instruction in recipe:
				currFeatures = classifierUtil.extractNGramFeatures(instruction, 4)
				for key in currFeatures:
					features[key] += currFeatures[key]

			value = classifierUtil.dotProduct(features, weights)
			print value
			if (signNumber(value) == -1):
				correctCount += 1
			total += 1
		print i
		print "Percentage Correct: ", float(correctCount)/total


# runs binary classifier by training on a dataset with K recipes and N ingredients, then tests against 30 fake recipes and outputs the percentage it got correct
binaryClassifier(100, 0)
