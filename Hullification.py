#This procedure makes use of a convex hull Sub routine

#(take inequalities example 2x1 + 4x3 ... = M -> parametric form
#Parametric simplification is pretty convenient suppose (Q1(x), Q2(x) ... QK(x)) is a parametric form and (T1(x), T2(x) ... TK(x)) is another
#Then we can very efficiently glue by solving Q(0) = T(0) + (d0 d1 ... dK) for d_i, then
#Q = Q_constant + Q(X_old), then Q_Constant and T(X_new) are glued through a new parameter F as above
#Then Inter(Q const, T(X_new)) + Q_(X_old) yields a parametrization of the new surface. ASsuming totally disjoint surfaces. What about non disjoint surfaces



#intersects it into a particular plane
#assuming ALL are in the <= form
def SpliceInequalities(InequalityVector, index, val):
	i = 0
	zao = len(InequalityVector)
	while i < zao:
		
		point = InequalityVector[i].pop(index)
		InequalityVector[i][len(InequalityVector[i]] -= point*value
		i+=1
	return InequalityVector

def 
