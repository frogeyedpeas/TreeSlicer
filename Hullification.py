from pulp import *
#This procedure makes use of a convex hull Sub routine

#FUCK THIS ALGORITHM
#IVE GONE INSANE BUILDING IT
#In life there are scientists
#They are content discovering what is and isn't
#THen there are engineers
#They seek to use waht they know to cause change
#I thought I was a scientist
#I'm secretly an Engineer
#Dont let them know
# - A poem

#(take inequalities example 2x1 + 4x3 ... = M -> parametric form
#Parametric simplification is pretty convenient suppose (Q1(x), Q2(x) ... QK(x)) is a parametric form and (T1(x), T2(x) ... TK(x)) is another
#Then we can very efficiently glue by solving Q(0) = T(0) + (d0 d1 ... dK) for d_i, then
#Q = Q_constant + Q(X_old), then Q_Constant and T(X_new) are glued through a new parameter F as above
#Then Inter(Q const, T(X_new)) + Q_(X_old) yields a parametrization of the new surface. ASsuming totally disjoint surfaces. What about non disjoint surfaces

#Lets make this version specific
#There are 0 <= x < = 1 Inequalities (n of htem)
#There are otherwise a list of non-attached inequalities
#We need to branch effectively that is, taking inequalities setting x_j = U, then 
# x_j <= 1, 0 <= x_j <= 0 -> x_j < 0, -x_j <0, x_j  #okay so we can splice like that 
#End reuslt, x_j = 0 -> 

#intersects it into a particular plane
#assuming ALL are in the <= form
#God knows what the user generates, needs to be cleaned of all (0000 1 ... 0) terms that match then this is fine
#Requires Copie of Inequality Vector Before Use
def SpliceInequalities(InequalityVector, index, val):
	i = 0
	zao = len(InequalityVector)
	while i < zao:
		
		point = InequalityVector[i][index]
		InequalityVector[i][index] = 0
		InequalityVector[i][len(InequalityVector[i])-1] -= point*val
		i+=1
	return InequalityVector
#Here we don't consider 
#We keep rows blank since during fusion this becomes simpler
#Ilevel is the top, pointlevel is hte bottom (stupid notation)
def interpolate(point, Inequality, pointlevel, Ilevel, j):
	#Each inequality represents a0x0  + ... a0xN <= targ
	#Consider a0x0 + ... a0XN = targ, this has a parametric form
	#So the parametric vector would be then ( (targ - a1x1 - .... xNxN)/a0, x1,x2 ... xN-1) 
	#Add this stage recall the vectors were depressed. So X_j needs to be set to 0 or 1. 
	#Now we add in the point P, set (x1 ... XN-1) in the previous example to 0
	#So we have P = (targ/a0,0,0....,0) + (d0,d1,d2 .... dN)P_n 
	#easy to solve so when P_n = 0, this is the same as before, if all else is 0, P_n = 1, we get this point
	#Then in parametric form we have ((targ - a1x1 - ..)/a0 + P0-targ/a0, x1 + P1xN, x2 + P2xN, ... XN-1 + PN-1XN) 
	#NOw this needs to be converted to regular form	for processing 	
	#Advanced method: (given a1x1 + a2x2 + a3x3 +a_(j-1) x_(j-1) + a_(j+1)x_(j+1) ... aNxN = beta, 	x'1 x'2 ... x'j-1 x'j+1 ... x'n 
	#WE note that resultant vector is (a1 a2 a3 ... a_(j-1) a_J ... aN Omega) 
	#Such that a_j W  = Omega - Beta
	# Ax' + a_j W2 = Omega 
	#Final formula is that: a_j(W1 - W2) = Ax' - Beta 
	#a_j = (Ax' - Beta)/(W1 - W2), and yet 
	#Omega = a_jW + Beta 
	i = 0
	obj = 0
	while i < len(point):
		obj += point[i]*Inequality[i]
		i+=1
	#that dot product^ could be made faster later	
	Inequality[j] = (obj - Inequality[len(Inequality)-1])/(Ilevel-pointlevel)	
#	Inequality.insert(j-1, (obj - Inequality[len(Inequality)-1])/(Ilevel-pointlevel))
	Inequality[len(Inequality)-1] += Inequality[j]*Ilevel

	return Inequality
def Optimize(objective, Inequalities,dimension):
	#array of variables needs to be generated
	Vararray = []
	i = 0
	while i < dimension:
		Vararray.append(LpVariable("x"+str(i),0,1)) # 0<= x_i <= 1
		i+=1

	prob = LpProblem("The_Problem",LpMaximize)

	for line in Inequalities:
		i = 0
		sr = 0
		while i < len(line)-1: #not including the bound
			sr += Vararray[i]*line[i]
			i+=1
		prob+=(sr<=line[len(line)-1]) #add the inequality IN
	i = 0
	obj = 0
	while i < len(objective):
		obj += (Vararray[i]*objective[i])
		i+=1
	prob+=obj #this is for optimization	

	status  = prob.solve() #solved the problem
	
	valuearray = []
	val = 0
	i = 0
	if status != -1:
		while i < dimension:
				
			valuearray.append(value(Vararray[i]))
	#		val += valuearray[i]*objective[i]
			i+=1

	print("objective " + str(objective) + " system: " + str(Inequalities) + " status: " + str(status)+ " value array: " + str(valuearray)+ " status: " + str(LpStatus[status]))

	return valuearray,val, status 


#Requires verification ahead of time
#Requires in general that Ilevel, pointlevel are given, as well as the index j across the merge 
#Generating "Cross List" of HULL
def Merge(FirstPiece, SecondPiece, pointlevel, Ilevel, j, dimension):
	CrossList = []
	#Need to generate layer constraint 
	for Inequalities in FirstPiece:
		temppoint,val,status= Optimize(Inequalities[:-1],SecondPiece, dimension) 
		CrossList.append(interpolate(temppoint,Inequalities, pointlevel, Ilevel, j))
		
	return CrossList

#Detects and removes Redundant Ones 
def clean(Inequalities, dimension):
	i = 0
	while i < len(Inequalities):
		temppoint,val, status = Optimize(Inequalities[i][:-1],Inequalities[:i]+Inequalities[i+1:], dimension)
		#status fails means the system is infeasible in the first place
		if status == -1:
			return False

		if val <= Inequalities[i][len(Inequalities[i])-1]:
			Inequalities.pop(i) #remove redundant constraint
			i-=1
		i+=1
	return Inequalities
def copy(inputarray):
	output = []
	i = 0
	while i < len(inputarray):
		output.append(inputarray[i])
		i+=1
	return output

def doubleLevelCopy(inputarray):
	output = []
	i = 0
	while i < len(inputarray):
		output.append(copy(inputarray[i]))
		i+=1
	return output
#So given a collection of inequalities we begin testing integer satisfiability
#Inequalities should be given as is
def CheckIntegerSatisfiability(Inequalities, dimension):
	i = 0
	testobj = []
	while i < dimension:
		testobj.append(1)
		i+=1
	point,val,status = Optimize(testobj,Inequalities, dimension)
	if status == -1:
		return "Failed"
	i = 0
	UpSystem = doubleLevelCopy(Inequalities)
	DownSystem = doubleLevelCopy(Inequalities)
	TrueDimension = dimension
		
	artificialconstraint1 = []
	artificialconstraint2 = []
	artificialconstraint3 = []
	artificialconstraint4 = []
	index = 0
	while index < dimension:
		artificialconstraint1.append(0)
		artificialconstraint2.append(0)
		artificialconstraint3.append(0)
		artificialconstraint4.append(0)
		index+=1
	artificialconstraint1.append(1)
	artificialconstraint2.append(-1)
	artificialconstraint3.append(0)
	artificialconstraint4.append(0)
	while i < dimension:
		#for each variable we begin hull procedure
		#during Cross generation: we don't want x = val constraints
		#suppose we do, we have x <= val, x >= val these would break the formula
		#would they? 
		#
		#We begin by branching:
		UpSystem = (SpliceInequalities(UpSystem, i, 1))
		DownSystem = (SpliceInequalities(DownSystem,i,0))
		#Now that we have branched we enter the clean up stage
		#UpSystem needs the constraint that x_i = 1
		
		artificialconstraint1[i] = 1
		artificialconstraint2[i] = -1
		artificialconstraint3[i] = 1
		artificialconstraint4[i] = -1

		
		
		#so now these components have been engineered:
		#Downsystem needs the constraint that x_i = 0
		
		UpSystem += [artificialconstraint1, artificialconstraint2]
		DownSystem += [artificialconstraint3, artificialconstraint4]
		
		UpSystem = clean(UpSystem, dimension)
		DownSystem = clean(DownSystem,dimension)

		#Now both systems are cleansed of redundant inequalities
		if UpSystem != False:
			if  DownSystem != False:
				
				UpSystem = UpSystem[:-2]
				
				TopCross = Clean(Merge(UpSystem,DownSystem,0, 1, i, dimension),dimension )
				DownSystem = DownSystem[:-2]
				UpSystem += [artificialconstraint1, artificialconstraint2]

				BottomCross =Clean( Merge(DownSystem,Upsystem,1,0,i, dimension), dimension)

				#Set them the same way
				UpSystem  = doubleLevelCopy(TopCross + BottomCross)
				DownSystem = doubleLevelCopy(TopCross + BottomCross)

			else:
				DownSystem = doubleLevelCopy(UpSystem)
				#TrueDimension-=1
		
		else:
			if DownSystem != False:
				
				UpSystem = doubleLevelCopy(DownSystem)
				#iTrueDimesion-=1
				
			else:
				return False #If both systems fail then the whole thing is infeasible
		#system spliced
		
		#Reset constants
		artificialconstraint1[i] = 0
		artificialconstraint2[i] = 0
		artificialconstraint3[i] = 0
		artificialconstraint4[i] = 0
		

		i+=1		

	return [True,UpSystem,DownSystem]
		
if __name__ == "__main__":
	#time to test 
	#Sample System

	InequalityList = [[1,1,1.2],[1,0,1],[-1,0,0],[0,1,1],[0,-1,0]]

	print(CheckIntegerSatisfiability(InequalityList,2))
