import random
import collections
import json
# Code from CS 221 assignment "scheduling"

class CSP:
    def __init__(self):
        # Total number of variables in the CSP.
        self.numVars = 0

        # The list of variable names in the same order as they are added. A
        # variable name can be any hashable objects, for example: int, str,
        # or any tuple with hashtable objects.
        self.variables = []

        # Each key K in this dictionary is a variable name.
        # values[K] is the list of domain values that variable K can take on.
        self.values = {}

        # Each entry is a unary factor table for the corresponding variable.
        # The factor table corresponds to the weight distribution of a variable
        # for all added unary factor functions. If there's no unary function for 
        # a variable K, there will be no entry for K in unaryFactors.
        # E.g. if B \in ['a', 'b'] is a variable, and we added two
        # unary factor functions f1, f2 for B,
        # then unaryFactors[B]['a'] == f1('a') * f2('a')
        self.unaryFactors = {}

        # Each entry is a dictionary keyed by the name of the other variable
        # involved. The value is a binary factor table, where each table
        # stores the factor value for all possible combinations of
        # the domains of the two variables for all added binary factor
        # functions. The table is represented as a dictionary of dictionary.
        #
        # As an example, if we only have two variables
        # A \in ['b', 'c'],  B \in ['a', 'b']
        # and we've added two binary functions f1(A,B) and f2(A,B) to the CSP,
        # then binaryFactors[A][B]['b']['a'] == f1('b','a') * f2('b','a').
        # binaryFactors[A][A] should return a key error since a variable
        # shouldn't have a binary factor table with itself.

        self.binaryFactors = {}

    def add_variable(self, var, domain):
        """
        Add a new variable to the CSP.
        """
        if var not in self.variables:
            self.numVars += 1
            self.variables.append(var)
            self.unaryFactors[var] = None
            self.binaryFactors[var] = dict()
            #raise Exception("Variable name already exists: %s" % str(var))
        self.values[var] = domain



    def get_neighbor_vars(self, var):
        """
        Returns a list of variables which are neighbors of |var|.
        """
        return self.binaryFactors[var].keys()

    def add_unary_factor(self, var, factorFunc):
        """
        Add a unary factor function for a variable. Its factor
        value across the domain will be *merged* with any previously added
        unary factor functions through elementwise multiplication.

        How to get unary factor value given a variable |var| and
        value |val|?
        => csp.unaryFactors[var][val]
        """
        factor = {val:float(factorFunc(val)) for val in self.values[var]}
        if self.unaryFactors[var] is not None:
            assert len(self.unaryFactors[var]) == len(factor)
            self.unaryFactors[var] = {val:self.unaryFactors[var][val] * \
                factor[val] for val in factor}
        else:
            self.unaryFactors[var] = factor

    def add_binary_factor(self, var1, var2, factor_func):
        """
        Takes two variable names and a binary factor function
        |factorFunc|, add to binaryFactors. If the two variables already
        had binaryFactors added earlier, they will be *merged* through element
        wise multiplication.

        How to get binary factor value given a variable |var1| with value |val1| 
        and variable |var2| with value |val2|?
        => csp.binaryFactors[var1][var2][val1][val2]
        """
        # never shall a binary factor be added over a single variable
        try:
            assert var1 != var2
        except:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '!! Tip:                                                                       !!'
            print '!! You are adding a binary factor over a same variable...                  !!'
            print '!! Please check your code and avoid doing this.                               !!'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            raise

        self.update_binary_factor_table(var1, var2,
            {val1: {val2: float(factor_func(val1, val2)) \
                for val2 in self.values[var2]} for val1 in self.values[var1]})
        self.update_binary_factor_table(var2, var1, \
            {val2: {val1: float(factor_func(val1, val2)) \
                for val1 in self.values[var1]} for val2 in self.values[var2]})

    def update_binary_factor_table(self, var1, var2, table):
        """
        Private method you can skip for 0c, might be useful for 1c though.
        Update the binary factor table for binaryFactors[var1][var2].
        If it exists, element-wise multiplications will be performed to merge
        them together.
        """
        if var2 not in self.binaryFactors[var1]:
            self.binaryFactors[var1][var2] = table
        else:
            currentTable = self.binaryFactors[var1][var2]
            for i in table:
                for j in table[i]:
                    assert i in currentTable and j in currentTable[i]
                    currentTable[i][j] *= table[i][j]

############################################################

# A backtracking algorithm that solves weighted CSP.
# Usage:
#   search = BacktrackingSearch()
#   search.solve(csp)
class BacktrackingSearch():

    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

        self.numIngredients = 0

        self.epsilon = 0.3

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
            #print self.optimalAssignment
        else:
            print "No solution was found."

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        return w

    def solve(self, csp, numIngredients, mcv = False, ac3 = False):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        self.numIngredients = numIngredients

        # Perform backtracking search.
        self.backtrack({}, 0, 1)
        probRandom = random.uniform(0.0,1.0)
        #print self.numAssignments
        if (probRandom <= self.epsilon):
            print "Epsilon greedy activated"
            print random.choice(self.allAssignments)
        # Print summary of solutions.
        self.print_stats()

    def backtrack(self, assignment, numAssigned, weight):
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """
        # print assignment 
        print self.numOperations
        self.numOperations += 1
        assert weight > 0

        if numAssigned == self.csp.numVars:

            # A satisfiable solution have been found. Update the statistics.
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:

                # checks if every spot is assigned
                toBeAssigned = [i for i in range(1, self.numIngredients * 2 + 1)]
                for k in assignment:
                    v = assignment[k]
                    if v != 0:
                        toBeAssigned.remove(v)
                if toBeAssigned:
                    return
                assignment = {k: v for k, v in newAssignment.items() if v > 0 and v <= 4 and k[0] != 'or'}
                #print "assignment and weight:"
                #print assignment
                #print weight

                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                else:
                    self.numOptimalAssignments = 1
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)
        # Get an ordering of the values.
        ordered_values = self.domains[var]

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
             
    
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    del assignment[var]
        else:
            # Arc consistency check is enabled.
            # Problem 1c: skeleton code for AC-3
            # You need to implement arc_consistency_check().
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values

                    #localCopy = copy.deepcopy(self.domains)
                    localCopy = self.domains.copy()
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.arc_consistency_check(var)

                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable.
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            # Problem 1b
            # Heuristic: most constrained variable (MCV)
            # Select a variable with the least number of remaining domain values.
            # Hint: given var, self.domains[var] gives you all the possible values
            # Hint: get_delta_weight gives the change in weights given a partial
            #       assignment, a variable, and a proposed value to this variable
            # Hint: for ties, choose the variable with lowest index in self.csp.variables
            # BEGIN_YOUR_CODE (our solution is 7 lines of code, but don't worry if you deviate from this)
            leastConsistentValues = float('inf')
            for var in self.csp.variables:
                if var not in assignment:
                    values = self.domains[var]
                    numConsistentValues = 0
                    for val in values:
                        if self.get_delta_weight(assignment, var, val) != 0:
                            numConsistentValues += 1
                    if numConsistentValues < leastConsistentValues:
                        leastConsistentValues = numConsistentValues
                        X = var
            return X




            # END_YOUR_CODE

    def arc_consistency_check(self, var):
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """
        # Problem 1c
        # Hint: How to get variables neighboring variable |var|?
        # => for var2 in self.csp.get_neighbor_vars(var):
        #       # use var2
        #
        # Hint: How to check if a value or two values are inconsistent?
        # - For unary factors
        #   => self.csp.unaryFactors[var1][val1] == 0
        #
        # - For binary factors
        #   => self.csp.binaryFactors[var1][var2][val1][val2] == 0
        #   (self.csp.binaryFactors[var1][var2] returns a nested dict of all assignments)

        # BEGIN_YOUR_CODE (our solution is 20 lines of code, but don't worry if you deviate from this)
        Xs = {var}
        while len(Xs) != 0:
            Xj = Xs.pop()
            domainXj = self.domains[Xj]
            for Xi in self.csp.get_neighbor_vars(Xj):
                domainXi = self.domains[Xi]
                newDomainXi = list(domainXi)
                for valueI in domainXi:
                    consistent = False
                    for valueJ in domainXj:
                        if self.csp.binaryFactors[Xi][Xj][valueI][valueJ] != 0:
                            consistent = True
                            break
                    
                    if consistent == False:
                        newDomainXi.remove(valueI)
                if newDomainXi != domainXi:
                    self.domains[Xi] = newDomainXi
                    Xs.add(Xi)   

class BeamSearch():

    #README
    #Most of the code is taken from backtracking search and the main change is that instead of keeping track of the current assignment, we keep a list
    # of all possible assignments we are considering. Beam() then recurses on a subset of those each time.

    #numOperations = 0
    #K = 0
    optimalAssignment = {}

    numOptimalAssignments = 0
    numAssignments = 0

            #how many layers of the tree basically
    numOperations = 0
    optimalWeight = 0

    firstAssignmentNumOperations = 0

    allAssignments = []
    K = 0
    started = False
    #attempt at adding human ingenuity

    epsilon = 0.3
    def initialize(self, number):
        self.K = number

    def reset_results(self):
        self.optimalAssignment = {}

        self.numOptimalAssignments = 0
        self.numAssignments = 0

        #how many layers of the tree basically
        self.numOperations = 0
        self.optimalWeight = 0
        self.firstAssignmentNumOperations = 0

        self.allAssignments = []

        self.numIngredients = 0

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print "Total number of assignments: %d" % (self.numAssignments)
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
            #print self.optimalAssignment
        else:
            print "No solution was found."

    def get_delta_weight(self, assignment, var, val):

        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        return w

    def solve(self, csp, numIngredients, mcv = False, ac3 = False):

        self.csp = csp
        self.mcv = mcv
        self.ac3 = ac3
        self.reset_results

        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        self.numIngredients = numIngredients

        self.beam([]) 
        prob = random.uniform(0.0,1.0)
        if (prob < self.epsilon):
            print random.choice(self.allAssignments)

        self.print_stats()

    def beam(self, currentPossibleAssignments): #list of tuples (current partial assignment, numberAssigned, weight) current partial assignment is a list of dictionaries

        print self.numOperations
        self.numOperations += 1
        #if (self.numOperations > 10): return
        newAssignmentsToChoose = []
        if (currentPossibleAssignments):
            for currentPartial in currentPossibleAssignments:
                currentAssignment, numberAssigned, weight = currentPartial
                if (numberAssigned == self.csp.numVars):
                    self.numAssignments += 1
                    newAssignment = {}
                    for var in self.csp.variables:
                        if (var in currentAssignment):
                            newAssignment[var] = currentAssignment[var]
                    self.allAssignments.append(newAssignment)
                    if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                        # checks if every spot is assigned
                        toBeAssigned = [i for i in range(1, self.numIngredients * 2 + 1)]
                        for k in currentAssignment:
                            v = currentAssignment[k]
                            if v != 0:
                                toBeAssigned.remove(v)
                        if toBeAssigned:
                            continue
                        assignment = {k: v for k, v in newAssignment.items() if v > 0 and v <= 4 and k[0] != 'or'}
                        # print "assignment and weight:"
                        # print assignment
                        # print weight

                        if weight == self.optimalWeight:
                            self.numOptimalAssignments += 1
                        else:
                            self.numOptimalAssignments = 1
                        self.optimalWeight = weight

                        self.optimalAssignment = newAssignment
                        if self.firstAssignmentNumOperations == 0:
                            self.firstAssignmentNumOperations = self.numOperations
                    return
                #this following code happens when the assignment is not complete yet
                variables = self.get_all_unassigned(currentAssignment)

                #currently ignoring ac3 and just doing regular beam search
                #try each combination of variable + value

                for var in variables:
                    ordered_values = self.domains[var]
                    for val in ordered_values:
                        deltaWeight = self.get_delta_weight(currentAssignment,var, val)
                        
                        if deltaWeight > 0:
                            currentAssignment[var] = val
                            newAssignmentsToChoose.append((dict(currentAssignment), numberAssigned + 1, weight * deltaWeight))
                           # print str(weight * deltaWeight)
                           # print newAssignmentsToChoose
                            del currentAssignment[var]
        elif not self.started: #when we are at beginning and there are no assignments to try yet
            self.started = True
            variables = self.csp.variables
            empty_dict = {}
            for var in variables:
                if type(var) is not str:
                    continue
                ordered_values = self.domains[var]
                for val in ordered_values:
                    #print val
                    deltaWeight = self.get_delta_weight(empty_dict,var, val)
                    
                    if deltaWeight > 0:
                        currentAssignment = empty_dict.copy()
                        currentAssignment[var] = val
                        newAssignmentsToChoose.append((dict(currentAssignment), 1, deltaWeight))
                        del currentAssignment[var]
            #print newAssignmentsToChoose
        #need to now pick the K best assignments and go from there
        #sorts by the weight
        newAssignmentsToChoose.sort(key = lambda tup:tup[2])
        #print "NEW ASSIGNMENTS"
        #print newAssignmentsToChoose

        bestOnes = newAssignmentsToChoose[len(newAssignmentsToChoose) - self.K:]
        #print bestOnes
        #recurses
        self.beam(bestOnes)



    def get_all_unassigned(self, assignment):
        unassigned = []

        for var in self.csp.variables:
            if (var not in assignment):
                unassigned.append(var)
        return unassigned



def get_or_variable(csp, name, variables, value):
    """
    Create a new variable with domain [True, False] that can only be assigned to
    True iff at least one of the |variables| is assigned to |value|. You should
    add any necessary intermediate variables, unary factors, and binary
    factors to achieve this. Then, return the name of this variable.

    @param name: Prefix of all the variables that are going to be added.
        Can be any hashable objects. For every variable |var| added in this
        function, it's recommended to use a naming strategy such as
        ('or', |name|, |var|) to avoid conflicts with other variable names.
    @param variables: A list of variables in the CSP that are participating
        in this OR function. Note that if this list is empty, then the returned
        variable created should never be assigned to True.
    @param value: For the returned OR variable being created to be assigned to
        True, at least one of these variables must have this value.

    @return result: The OR variable's name. This variable should have domain
        [True, False] and constraints s.t. it's assigned to True iff at least
        one of the |variables| is assigned to |value|.
    """
    result = ('or', name, 'aggregated')
    csp.add_variable(result, [True, False])

    # no input variable, result should be False
    if len(variables) == 0:
        csp.add_unary_factor(result, lambda val: not val)
        return result

    # Let the input be n variables X0, X1, ..., Xn.
    # After adding auxiliary variables, the factor graph will look like this:
    #
    # ^--A0 --*-- A1 --*-- ... --*-- An --*-- result--^^
    #    |        |                  |
    #    *        *                  *
    #    |        |                  |
    #    X0       X1                 Xn
    #
    # where each "--*--" is a binary constraint and "--^" and "--^^" are unary
    # constraints. The "--^^" constraint will be added by the caller.
    for i, X_i in enumerate(variables):
        # create auxiliary variable for variable i
        # use systematic naming to avoid naming collision
        A_i = ('or', name, i)
        # domain values:
        # - [ prev ]: condition satisfied by some previous X_j
        # - [equals]: condition satisfied by X_i
        # - [  no  ]: condition not satisfied yet
        csp.add_variable(A_i, ['prev', 'equals', 'no'])

        # incorporate information from X_i
        def factor(val, b):
            if (val == value): return b == 'equals'
            return b != 'equals'
        csp.add_binary_factor(X_i, A_i, factor)

        if i == 0:
            # the first auxiliary variable, its value should never
            # be 'prev' because there's no X_j before it
            csp.add_unary_factor(A_i, lambda b: b != 'prev')
        else:
            # consistency between A_{i-1} and A_i
            def factor(b1, b2):
                if b1 in ['equals', 'prev']: return b2 != 'no'
                return b2 != 'prev'
            csp.add_binary_factor(('or', name, i - 1), A_i, factor)

    # consistency between A_n and result
    # hacky: reuse A_i because of python's loose scope
    csp.add_binary_factor(A_i, result, lambda val, res: res == (val != 'no'))
    return result     

def separateIngredients(sentence, listOfIngredients):
    returnList = []
    for x in range(len(sentence)):
        if (sentence[x] in listOfIngredients):
            returnList.append(sentence[x])

    return returnList

def generateFeatureWeights(listOfIngredients):
    featuresWeightsDict = collections.defaultdict(float)
    dictionaryInstructions = {}
    fileName = "full_format_recipes.json"
    with open(fileName, 'r') as f:
        dictionaryInstructions = json.load(f)
    #print dictionaryInstructions[1][u'directions']

    with open('cooking_verbs.txt') as f:
        verbs = f.readlines()
    verbs = [x.strip() for x in verbs]
    
    ingredients = listOfIngredients

    for i in range(1, len(dictionaryInstructions)):
        #print dictionaryInstructions[i].keys()
        if (u'directions' in dictionaryInstructions[i]):
            for instruction in dictionaryInstructions[i][u'directions']:
                instruction = instruction.lower()
                sentenceWords = instruction.split()
                relevantVerbs = set.intersection(set(verbs), set(sentenceWords))
                relevantIngredients = set.intersection(set(ingredients), set(sentenceWords))

                for j in relevantVerbs:
                    for k in relevantIngredients:
                        featuresWeightsDict[(j, k)] += 1

                #for l in relevantIngredients:
                 #   for m in relevantIngredients:
                  #      if (l != m):
                   #         featuresWeights[(l,m)] += 1

                ingredientsInList = separateIngredients(sentenceWords, listOfIngredients)

                for l in range(len(ingredientsInList)):
                    for m in range(l + 1, len(ingredientsInList)):
                        featuresWeightsDict[(l,m)] += 1

    print featuresWeightsDict
    return featuresWeightsDict

def evaluationFunction(assignment, listOfIngredients):

    #determines how real a recipe is, the higher the return value, the more genuine the recipe
    realness = 0
    #generate features and weights

    featuresWeights = generateFeatureWeights(listOfIngredients)
    currentVerbIndex = 1
    currentIngredientIndex = 2
    while (assignment and currentIngredientIndex <= len(assignment)):
        currentVerb = None
        currentIngredient = None
        for key in assignment:
            if assignment[key] == currentVerbIndex:
                currentVerb = key
            if assignment[key] == currentIngredientIndex:
                currentIngredient = key
            if (currentIngredient and currentVerb):
                break
        realness += featuresWeights[(currentVerb, currentIngredient)]
        currentVerbIndex += 2
        currentIngredientIndex += 2

    orderedListIngredients = []
    currentIngredientIndex = 2
    while (currentIngredientIndex < len(assignment)):
        currentIngredient = None
        for key in assignment:
            if assignment[key] == currentIngredientIndex:
                currentIngredient = key
                break
        orderedListIngredients.append(currentIngredient)
        currentIngredientIndex += 2

    for x in range(len(orderedListIngredients)):
        for y in range(x + 1, len(orderedListIngredients)):
            realness += featuresWeights[(x, y)]
        
    return realness

