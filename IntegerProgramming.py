from pulp import *
from math import *
from copy import *
import requests
#This will be a collection of integer programming algorithms
#1. Rounding Schemes
#   Either through independent derivation
#   Max Max Max .... (to determine bounds)
#   Auto-Derivation (x+y+Z) <=2 (x+y-z) <= 1-> x+y <= 1 (done)
#       Point Seperation (Gomory's cutting planes)
#2. Branching Schemes
#3. Algebraic Control schemes
#   Consider: (x+y+z) <= 2, (x+y-z) <= 0 (x+y+z)(x+y-z) <= 0
# Etc... we can create higher level algebraic abstractions
# Note that x^n = x for x in 0,1
# x^2 + y^2 + z^2 <= 2 -> x+y+z<=2 (a tighter bound)


QuickSetup = '''
#pulpTestAll()

x1 = LpVariable("x1",0,40) #0 <= x1 <= 40
x2 = LpVariable("x2",0,1000) #0 <= x2 <= 1000
prob = LpProblem("Problem",LpMaximize) #declare prob name and type

#prob += equation

# defines the constraints
prob += 2*x1+x2 <= 100 
prob += x1+x2 <= 80
prob += x1<=40
prob += x1>=0
prob += x2>=0
 
# defines the objective function to maximize
prob += 3*x1+2*x2
 
# solve the problem
status = prob.solve()
print "hi"
print LpStatus[status]
 
# print the results x1 = 20, x2 = 60
print value(x1)
print value(x2)
'''

#algorithm psuedo-code
# we generate a list of consttraints. Given N variables
# consider the N partitions of N (there's only 1)
# consider the N partitions of N+1 (N 1)
# N+2 -> (N 2) + (N 1)
# N+3 -> (N 3) + (N 2)*2 + (N 1)
# N+4 -> (N 4) +  etc...
# as the constraints are added sequentially verify that that all the current constraints are tight, + gomory's cut since if B is not || to Q, then under integrality, we can slice of B-tip, 
# why is this expected to work?
# they are all very similar constraints, and


x = {}
x[1] = [1]
x[2] = [[2],[1,1]]

def planeGenerate(indexList, planarList, splane):
    
    indexList[0] = 0
    while indexList[0] < len(splane):
        t = copy(splane)
        t[indexList[0]]+=1
        if len(indexList) > 1:   
            planeGenerate(indexList[1:],planarList,t)
        else:
            planarList.append(t)
        indexList[0]+=1
    return planarList

def parallelPlanes(splane, di):
    u = []
    i = 0
    while i < di:
        u.append(0)
        i+=1
    i = 0
    planars = []
    planeGenerate(u,planars,splane)
    return planars



def AnIPsolver(constraints, obj): #objective function must contain integer terms (adjust it so that is the case)
    #we make a copy of the constraints so as to not lose them
    A1 = copy(constraints)
    A2 = copy(constraints)
    #we generate temporary maxes and mins
    cmax = probGenerate(A1, obj, 'Max') #get the current max
    cmin = probGenerate(A2, obj, 'Min') #get the current min
    currentmax = cmax[2]
    currentmin = cmin[2]
  
    currentsolution = 0
    while True:
        if (currentmax- currentmin) < 1: #if these two planes get within distance 1 of each other, then there really won't be an integer point 
            return [currentsolution,temptarg]
        temptarg = (currentmax + currentmin)/2
        #we make a shallow copy of the constraints
        tconstraint = copy(constraints)
        #we then slice the set by adding in the expected performance we desire
        tconstraint += [obj + [-1]+[temptarg]] #add on the bound obj >= thisvalue
        #now we check for an integer solution
        endresult = autoSolver(tconstraint)
        if endresult[0] == 'No Integer Solution': #this is too tight of a bound
            currentmax = temptarg #there is nothing with a max greater than this so we can set it to the middle

        if endresult[0] == 'Integer Solution Discovered':
            currentmin = temptarg+1 #we expect at least this much performance so something slightly tighter is given
            currentsolution = endresult[1:] #grab the value array along with objective value
            
               

def autoSolver(constraints):
    i = len(constraints[0])-3 #getting the obj (note here the -3 = -2 (for inequ + val) and -1 for end of list 
    
    #set up the list of cuts to maintain
    objlist = []
    #meta will contain whether a cut has been visited and the best value
    #meta will also contain whether a cut has been 
    meta = [] 
    #set up the first one x1 + x2 + x3 ... xN 
    objlist.append([])
    meta.append([]) 
    while i > -1:
        objlist[0].append(1)
        i-=1
    meta[0] = [len(objlist),False] #initialized value

   
 
    while True:
        #print "current objectives: ", objlist
        i = 0
        #for each of the cuts

        generatorFlag = True #this if still True indicates we need to go back to the top
        while i < len(objlist):
            
            #print constraints
            t = probGenerate(constraints, objlist[i],'Max')
            
            if t[0] == 'Infeasible':
                #print "Constraints Used: ", objlist
                #print "Bounds on Constraints: ", meta
                return ['No Integer Solution',t]
            j = 0
            flag = True
         
            while j < len(t[1]): #this stage could benfit from G-Cut
                if floor(t[1][j])!=t[1][j]:
                    flag = False
                j+=1
            if flag:
                #print "Constraints Used: ", objlist
                #print "Bounds on Constraints: ", meta
                return ['Integer Solution Discovered',t]

            #no integer solution detected ,will implement point cuts ex: gomory at a later date
            
            #add new found constraint

            if meta[i][0] != floor(t[2]): #a value change occurred:
                print "We are rounding:", meta[i][0], floor(t[2])
                x = objlist[i] + [1] + [floor(t[2])]
                constraints += [x]
                meta[i][0] = floor(t[2]) #set the new default bound
                generatorFlag = False
                #i = -1 #go back to the start
            
            i+=1

       
    
        #we processed everything and reached the end time to expand the search space
        if generatorFlag:
            i = 0
            while i < len(meta):
                if meta[i][1] == False: #unexplored region discovered
                    meta[i][1] = True #we set the region to found
                    z =  parallelPlanes(objlist[i],1) #add set of parallel planes
                    for planes in z: #setting up new points for potential search at the tail
                        meta.append([meta[i][0]+1,False])
                    objlist = objlist + z #added the planes to tail
                    break #get out of here!

                i+=1
        print "currently  we have:", len(objlist), "cuts being processed"
            
            
            
            
        

def probGenerate(constraints, obj, ty):

    #in principle the constraints need not even be of integer form, so i'm not going to bother too much with them just yet 
    
    t = constraints[0] #grab the first constraint
    size = len(t)-2 #varcount is less than "sign" and less than "tail"

    #generate variables
    #set up the array
    vararray = []
    #this while loop will instert a variable for each corresponding element
    i = 0
    while i < size: 
        vararray.append(LpVariable("x"+str(i),0,1)) #so far we stick iwth 0-1 variables
        i+=1
    #we have either maximization or minimization problems the max branch is direct
    prob = 0 #placeholder to account for nested access
    if ty == 'Max':
        prob = LpProblem("Problem",LpMaximize)
    elif ty == 'Min':
        prob = LpProblem("Problem", LpMinimize)
    else:
        print "error" #ty didn't have the right type of value

    #now we add the constraints

    #print constraints
    for constraint in constraints:
        i = 0
        tau = 0
        #we add var[i]*coeff[i] to tau
        while i < len(constraint)-2:
            
            
            tau += vararray[i]*constraint[i]
            i+=1
        #determine the type of inequality
        if constraint[i] == 1:
            prob += tau<=constraint[i+1]
        elif constraint[i] == 0:
            prob += tau==constraint[i+1]
        elif constraint[i] == -1:
            prob += tau>=constraint[i+1]

    #now add the objective function
    tau = 0
    i = 0
    while i < len(obj):
        #print vararray, " ", obj, i
        tau += vararray[i]*obj[i]
        i+=1
    prob += tau

    status = prob.solve() #get the status

    #values for individual inspection
    valuearray = []
    i = 0
    while i < len(vararray):
        valuearray.append(value(vararray[i]))
        i+=1

    #this also outputs the value of the expression tau, which was our objective
    return [LpStatus[status],valuearray, value(tau)] 
    

#sample question
constraints1 = [[2,3,1,4],[4,5,-1,5],[1,-1,1,0.9]]

#next sample 3d cube missing each vertex
constraints2 = [[1,1,1,1,2.9],[1,1,-1,1,1.9],[1,-1,1,1,1.9],[-1,1,1,1,1.9],[1,-1,-1,1,0.9],[-1,1,-1,1,0.9],[-1,-1,1,1,0.9],[1,1,1,-1,.1]]

constraints25 =  [[1,1,1,1,2.9],[1,1,-1,1,1.9],[1,-1,1,1,1.9],[-1,1,1,1,1.9],[-1,1,-1,1,0.9],[-1,-1,1,1,0.9]]
#next sample 4d cube between strange range
constraints3 = [[1,2,3,4,5,1,6.9],[1,2,3,4,5,-1,6.8]]
#print autoSolver(constraints25)

#A sample knapsack problem
constraintsKnapsack=[[4,7,3,4,6,3,3,1,10]]
objKnapsack = [10,23,21,19,11,5,8]

#lets make an NP complete problem of choice
constraintsKnapsack2 = [[7,6,8,9, 1, 18]]
objknapsack2 = [7,6,8,9]

#Knapsack Major Test 1
cs1 = [[23,31,29,44,53,38,63,85,89,82,1,165]]
ob1 = [92,57,49,68,60,43,67,84,87,72]

#knapsack Major Test 2

f = open('p08_c.txt','r')
capacity = int(f.read())
f.close()

f = open('p08_w.txt','r')
weights = f.read().split() #split by white space
i = 0
while i < len(weights):
    weights[i] = int(weights[i])
    i+=1
f.close()

f = open('p08_p.txt','r')
obj = f.read().split()
i = 0
while i < len(obj):
    obj[i] = int(obj[i])
    i+=1
f.close()



cs2 = [weights + [1] + [capacity]]

print AnIPsolver(cs2,obj)

garbage = '''
x1 = LpVariable("x1",0,1)
x2 = LpVariable("x2",0,1)
prob = LpProblem("Problem",LpMaximize) #declare prob name and type
obj = x1-x2
prob += x1+x2==0.9
#prob += x1+x2<=0.3
prob += obj


    
status = prob.solve()
print LpStatus[status]
print value(x1)
print value(x2)
print value(obj)

'''




