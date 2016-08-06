from pulp import *
#This procedure makes use of a convex hull Sub routine

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
		
		point = InequalityVector[i].pop(index)
		InequalityVector[i][len(InequalityVector[i])-1] -= point*val
		i+=1
	return InequalityVector
#Here we don't consider 
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

	Inequality.insert(j-1, (obj - Inequality[len(Inequality)-1])/(Ilevel-pointlevel))
	Inequality[len(Inequality)-1] += Inequality[j]*Ilevel

	return Inequality
def Optimize(objective, Inequalities,dimension):
	#array of variables needs to be generated
	Vararray = []
	i = 0
	while i < dimension:
		Vararray.append(LpVariable("x"+str(i),0,1) # 0<= x_i <= 1
		i+=1

	prob = LpProblem("The_Problem",LpMaximize)

	for line in Inequalities:
		i = 0
		sr = 0
		while i < len(line)-1: #not including the bound
			sr += Vararray[i]*line[i]
			i+=1
		prob+=(sr<=line[len(line)-1]) #add the inequality IN

	status  = prob.solve() #solved the problem

#Requires verification ahead of time
#Requires in general that Ilevel, pointlevel are given, as well as the index j across the merge 
#Generating "Cross List" of HULL
def Merge(FirstPiece, Second Piece, pointlevel, Ilevel, j):
	CrossList = []
	for Inequalities in FirstPiece:
		temppoint,val = Optimize(Inequalities[:-1],SecondPiece) 
		CrossList.append(interpolate(temppoint,Inequalities, pointlevel, Ilevel, j))
		
	return CrossList





#Detects and removes Redundant Ones 
def Clean(Inequalities):
	i = 0
	while i < len(Inequalities):
		temppoint,val = Optimize(Inequality[i],Inequalities)
		if val < Inequalities[i][len(Inequalities[i])-1]:
			Inequalities.pop(i) #remove redundant constraint
			i-=1
		i+=1
	return Inequalities

