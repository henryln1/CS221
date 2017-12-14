import random
import recipeUtil 
from trainOnRecipes import *

def main(listOfIngredients, allrecipeinstructions):
    assignment = {}
    numIngredients = len(listOfIngredients)
    with open('cooking_verbs.txt') as f:
        verbs = f.readlines()
    verbs = [x.strip() for x in verbs]

    ingredientIndices = [i for i in range(2, numIngredients * 2 + 1, 2)]
    verbIndices = [i for i in range(1, numIngredients * 2 + 1, 2)]

    for ingredient in listOfIngredients:
        index = random.randint(0, len(ingredientIndices) - 1)
        assignment[ingredient] = ingredientIndices[index]
        ingredientIndices.remove(ingredientIndices[index])

    for verbIndex in verbIndices:
        verb = random.randint(0, len(verbs) - 1)
        assignment[verbs[verb]] = verbIndex
        verbs.remove(verbs[verb])


    order = ['' for i in range(len(assignment) + 1)]
    for x in assignment:
        order[assignment[x]] = x

    i = 1
    j = 1
    while i < len(assignment):
        print str(j) + '. ' + order[i] + ' ' + order[i + 1]
        i += 2
        j += 1

    k = recipeUtil.evaluationFunction(assignment, listOfIngredients, True)
   
    return k
