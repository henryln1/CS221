import time
#import pandas
import random
import collections
import sys
import math
import json
import trainOnRecipes
import baseline
import csv


def readCSV(inputfile):
	#inputInformation = pandas.read_csv(inputfile)
	# allIngredientsPlusOtherThings = []
	# recipes = collections.defaultdict(collections.defaultdict(int)) #maps a recipe title to a list of ingredients needed
	# allColumns = []
	# nutritionalValueRecipe = collections.defaultdict(list) #maps recipe to nutritional value
	# for ingredient in inputInformation: #this iterates through all the colum titles, but it is important to note that there are things that are not ingredients included
	# 	if (ingredient != 'title' and ingredient != 'ratings' and ingredient != 'calories' and ingredient != 'protein' and ingredient != 'fat' and ingredient != 'sodium'):
	# 		allIngredientsPlusOtherThings.append(ingredient)
	# 	allColumns.append(ingredient)
	# numberOfRecipesRead = 0
	# for index, row in inputInformation.iterrows(): #goes through the list and stores the ingredients for each dish
	# 	recipeName = row['title']
	# 	for currentEntry in allIngredientsPlusOtherThings:
	# 		if row['currentEntry'] != 0:
	# 			recipes[recipeName][currentEntry] = row['currentEntry'] #adds it to the list of ingredients if it is present in the ingredient list
	# 	numberOfRecipesRead += 1
	# print "numberOfRecipesRead: ", numberOfRecipesRead
	# print "hello"
	# commented out above since isn't currently needed
	recipes = []
	return recipes

def readIngredients(input): #reads the ingredient.txt in as a list
	with open(input) as f:
		content = f.readlines()
	content = [x.strip() for x in content]
	return content

def readInstructions(input):
	data = json.load(open(input))
	allrecipeinstructions = []
	for recipe in data:
		if len(recipe)!= 0:
			directions = recipe["directions"]
			allrecipeinstructions.append(directions)
	return allrecipeinstructions
	
	
def main(args):
	if (len(sys.argv) < 4 or len(sys.argv) > 5):
		print "Please provide 3 parameters, or 4 if you want to run the baseline model."
		raise Exception("Usage: readData.py <inputfile>.csv <inputinstructions>.json <ingredientList>.txt -b")
	
	print "This program will read in the csv file and generate data structures to hold the information. \
	 It then looks at the ingredient list passed in and tries to generate a list of instructions to make a dish \
	 using those recipes."
	inputfile = args[0]
	instructions = args[1]
	ingredientList = args[2]
	recipesDict = readCSV(inputfile)
	listOfIngredients = readIngredients(ingredientList)
	instructions = readInstructions(instructions)
	if len(sys.argv) == 4:
		trainOnRecipes.main(listOfIngredients, instructions)
	else:
		baseline.main(listOfIngredients, instructions)

#picks a random set of ingredients and generated a random list of instructions to return. 

def generateFakeRecipe():
	instructions = readInstructions("full_format_recipes.json")

	#file with the list of possible recipes to choose from
	file = open('allIngredients.txt', 'r')
	allIngredients = file.readlines()
	file.close()

	allIngredients = [x for x in allIngredients if x != '\n']
	for b in range(len(allIngredients)):
		allIngredients[b] = allIngredients[b][:-1]

	#how many ingredients we want
	#numberOfIngredients = random.randint(1, len(allIngredients))
	numberOfIngredients = random.randint(1,7)
	#choose which ingredients we're using
	recipeIngredients = random.sample(allIngredients, numberOfIngredients)
	assignment, valueCSP = trainOnRecipes.main(recipeIngredients, instructions, True)
	generatedInstructions = trainOnRecipes.translateAssignment(numberOfIngredients, assignment, True)

	returnList = []
	for i in range(len(generatedInstructions)):
		currString = generatedInstructions[i]
		currString = currString[3:]
		currString = currString[:-1]
		returnList.append(currString)
	return returnList

#generate K fake recipes and returns a list of lists
def generateKFakeRecipes(K):
	returnList = []
	for i in range(K):
		returnList.append(generateFakeRecipe())
	print returnList
	return returnList


def generateExcelFile():
	instructions = readInstructions("full_format_recipes.json")

	file = open('allIngredients.txt', 'r')
	allIngredients = file.readlines()
	file.close()

	allIngredients = [x for x in allIngredients if x != '\n']
	for b in range(len(allIngredients)):
		allIngredients[b] = allIngredients[b][:-1]
	print allIngredients

	file = open("generatedData.txt","a+")
	file.write("number of ingredients, evalCSP, evalBaseline" + "\n")
	for g in range(1, 11):
		for i in range(10):
			currentIngredients = random.sample(allIngredients, g)
			valueCSP = trainOnRecipes.main(currentIngredients, instructions)
			valueBaseline = baseline.main(currentIngredients, instructions)
			#csv.write(str(g) + "," + str(valueCSP) + "," + str(valueBaseline) + "\n")
			print "valueCSP", valueCSP
			print "valueBaseline", valueBaseline
			file.write(str(g) + "," + str(valueCSP) + "," + str(valueBaseline) + "\n")
	file.close()
if __name__ == '__main__':
	args = sys.argv[1:]
	main(args)

