from copy import *
def PartitionMachine(n):
    a = [0 for i in range(n+1)]
    k = 1
    y = n-1
    while k != 0:
        x = a[k-1]+1
        k-=1
        while 2*x <= y:
            a[k] = x
            y -= x
            k+=1 
        l = k+1
        while x <= y:
            a[k] = x
            a[l] = y
            yield a[:k+2]
            x+=1
            y -= 1
        a[k] = x+y
        y = x+y-1
        yield a[:k+1]



def getPartitions(n,x,cap):
    try:
        return x[n]
    except:
        
        w = PartitionMachine(n)
        print "they were made"
        z =[]
        while True:
            try:
                a = w.next()
                if len(a) < cap:
                    z.append(a)
            except:
                x[n] = z
                print z
                return z

def permuteList(elist): #generates every unique permutation
    tdict = {}
    olist = []
   
    if len(elist) <= 1:
        return [elist]
    for items in elist:
        templist = copy(elist)
        try:
            a = tdict[items]
        except:
            templist.remove(items)
            submutations = permuteList(templist) #grab all but the current item   
            for things in submutations:
                olist.append([items]+things)
            tdict[items] = 0
   
    return olist


def getPermutedPartitions(n,x,cap): #cap indicates max size non inclusive
    parts = getPartitions(n,x,cap)
    out = []
    for pieces in parts:
        if len(pieces) < cap:
           
            out += permuteList(pieces + ((cap - len(pieces))-1)*[0])
    return out

x = {}
print getPermutedPartitions(5,x,10)
    
