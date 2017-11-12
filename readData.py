import time
import pandas
import random
import collections
import sys
import math

#hi
#hi

def readCSV(inputfile):
	inputInformation = pandas.read_csv(inputfile):
	allIngredientsPlusOtherThings = []
	recipes = collections.defaultdict(collections.defaultdict(int)) #maps a recipe title to a list of ingredients needed
	allColumns = []
	nutritionalValueRecipe = collections.defaultdict(list) #maps recipe to nutritional value
	for ingredient in inputInformation: #this iterates through all the colum titles, but it is important to note that there are things that are not ingredients included
		if (ingredient != 'title' and ingredient != 'ratings' and ingredient != 'calories' and ingredient != 'protein' and ingredient != 'fat' and ingredient != 'sodium'):
			allIngredientsPlusOtherThings.append(ingredient)
		allColumns.append(ingredient)
	numberOfRecipesRead = 0
	for index, row in inputInformation.iterrows(): #goes through the list and stores the ingredients for each dish
		recipeName = row['title']
		for currentEntry in allIngredientsPlusOtherThings:
			if row['currentEntry'] != 0:
				recipes[recipeName][currentEntry] = row['currentEntry'] #adds it to the list of ingredients if it is present in the ingredient list
		numberOfRecipesRead += 1
	print "numberOfRecipesRead: ", numberOfRecipesRead
	return recipes

def readIngredients(input): #reads the ingredient.txt in as a list
	with open(input) as f:
		content = f.readLines()
	content = [x.strip() for x in content]
	return content


def main():
	if (len(sys.argv) != 3):
		raise Exception("Usage: readData.py <inputfile>.csv <ingredientList>.txt")
	print "This program will read in the csv file and generate data structures to hold the information. \
	 It then looks at the ingredient list passed in and tries to generate a list of instructions to make a dish \
	 using those recipes."
	inputfile = sys.argv[1]
	ingredientList = sys.argv[2]
	recipesDict = readCSV(inputfile)
	listOfIngredients = readIngredients(ingredientList)

	#do things and analyze

