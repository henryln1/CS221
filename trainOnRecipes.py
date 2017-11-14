# this runs inside the main of getData and thus has acess to the variables
# needs to have the cumulative ingedients list, the directions for each recipe, and a list of verbs used for cooking

import recipeUtil.py

def createCSP():
  csp = recipeUtil.CSP()
  # add variable for each ingredient in cumulative ingredients list
  # iterate over each sentence in directions 
  # - identify ingredients in sentence
  # - identify verbs in sentence
  # - add binary factor for each ingredient in each sentence and verbs in sentence
  
  
