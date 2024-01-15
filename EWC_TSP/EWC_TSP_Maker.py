import requests
import csv
import networkx


#helper get a jsons of a route
def getLeg(dists,coords,fold,s,d):
    rte=''
    with open(r'C:\Users\jdeur\OneDrive\Documents\TSP_Projs\\'+fold+'\\'+str(s)+'to'+str(d)+'.txt','w') as edfl:
        rte=requests.get('http://router.project-osrm.org/route/v1/driving/'+townL[s][2]+','+townL[s][3]+';'+townL[d][2]+','+townL[d][3]+'?overview=simplified&geometries=geojson')
        rte=rte.json()
        rte=str(rte["routes"][0]["geometry"])
        rte=rte.replace("'",'"')
        edfl.write(rte)
        edfl.close()
    return

#helper to cut a tour
#should get a call
def cutTour(dists,walk,fold):
    WlkOrd =[]
    cutWlkLen=0
    lst=-1
    for i in walk:
        if i not in WlkOrd:
            if len(WlkOrd)>=1:
                print(str(i)+','+str(lst))
                cutWlkLen+=dists[i][lst]
                getLeg(dists,coords,fold,i,lst)
            WlkOrd.append(i)
            lst=i
    #print("Walk order: "+str(sorted(WlkOrd)))
    cutWlkLen+=dists[WlkOrd[0]][lst]
    getLeg(dists,coords,fold,WlkOrd[0],lst)
    print("Cut tour:"+str(cutWlkLen)+" seconds")
    h=cutWlkLen/3600
    d=h/8
    print("That is "+str(h)+" hours and "+str(d)+" 8 hour days")
    return WlkOrd

#Choose between the National or Provincial mode
m=0
#TO DO: Make it so strings in the script do not need to be changed to do different loops
while True:
    m=input(
        "Federal or Provincial loop? \n1. Federal \n2. Provincial\n"
        )
    if(m!='1' or m!='2'):
        break  

#Use open-spource routing machine to generate the matrix

if m=='2':
    #This string changes the provincial tour used
    p=""
    prov_dict={'1':"BC",'2':"AB",'3':"SK",'4':"MB",'5':"ON",'6':"QC",'7':"ATL"}
    while True:
        i=input("Which Province?\n1:BC\n2:AB\n3:SK\n4:MB\n5:ON\n6:QC\n7:ATL\n")
        if i in prov_dict:
            p=prov_dict[i]
            print(p)
            break
        else:
            continue
    with open(r'C:\Users\jdeur\OneDrive\Documents\TSP_Projs\\'+p+'_Towns.csv') as townsf:
        townRead=csv.reader(townsf)
        townL=[]
        count=0
        #Generate Townlist and coordinate list
        for f in townRead:
            if count!=0:
                townL.append(f)
            count+=1;
        coords=""
        for i in range(len(townL)):
            coords=coords+townL[i][2]+','+townL[i][3]+';'
        coords=coords[:-1]
else:
    with open(r'C:\Users\jdeur\OneDrive\Documents\TSP_Projs\\EWC_Towns_Driveable.csv') as townsf:
        townRead=csv.reader(townsf)
        townL=[]
        count=0
        #Generate Townlist and coordinate list
        for f in townRead:
            if count!=0:
                townL.append(f)
            count+=1;
        coords=""
        for i in range(len(townL)):
            coords=coords+townL[i][2]+','+townL[i][3]+';'
        coords=coords[:-1]
        
#USE THE TABLE SERVICE INSTEAD
req=requests.get('http://router.project-osrm.org/table/v1/driving/'+coords)
if(str(req)=="<Response [200]>"):
    #get the dist
    js=req.json()
    dists=js["durations"]
else:
    print("failed")
if len(townL)>15:
    print("List of towns is too big for DP algortihm...usings a couple of approximations")    
    #Appoximation using prims, getting a MST
    visited=[0]
    mst=networkx.Graph()
    mstSz=0
    for i in range(1,len(townL)):
        visited.append(i)
        minD=-1
        s=-1
        d=-1
        for j in range(len(visited)):
            if minD==-1 or minD>dists[i][j] and i != j:
                minD=dists[i][j]
                s=i
                d=j
            else:
                continue
        mstSz+=minD
        mst.add_edge(s,d,weight=minD)
        print("Go from "+townL[s][0]+" to "+townL[d][0])
        getLeg(dists,coords,"MST",s,d)
    print("MST size:"+str(mstSz))

    #make it at tour
    eulMst = networkx.eulerize(mst)
    mstWalk = [u for u ,v  in networkx.eulerian_circuit(eulMst)]
    cutTour(dists,mstWalk,"MST_Cut")

        
    #Approximation using Christofides
    #Get odd-degree
    oddeg=[]
    for i in mst.nodes:
        print(townL[i][0]+" has a degree of "+str(mst.degree[i]))
        if(mst.degree[i]%2==1):
            oddeg.append(i)
    print(str(len(oddeg))+" odd degree towns")
    odds=networkx.Graph()
    for i in oddeg:
        for j in oddeg:
            if i != j:
               odds.add_edge(i,j,weight=-1*dists[i][j])
               print(odds.get_edge_data(i,j))
    #To-do fix min-weight perfect matching
    oddmatch=networkx.max_weight_matching(odds,maxcardinality=True)
    print(oddmatch)
    christo=networkx.MultiGraph(mst)
    for i in oddmatch:
        #verify that weights need to be corrected
        getLeg(dists,coords,"OddMatch",i[0],i[1])
        christo.add_edge(i[0],i[1],weight=dists[i[0]][i[1]])
        print(str(townL[i[0]][0])+" to "+str(townL[i[1]][0]))
    #verify that all towns have an even degree
    for i in christo:
        print(townL[i][0]+" has a degree of "+str(christo.degree[i]))
    #Ensure this differnt from the eulerian MST
    christwalk=[u for u ,v  in networkx.eulerian_circuit(christo)]
    cutTour(dists, christwalk, "christWalk")
    #to-do Add other algorithms
#DP up to 15
else:
    print("Using DP algorithm")
    sol=[0]
    #Make a dict to store a subset and the next thing in the path
    setdex={}
    def heldKarp(S,v):
        if len(S)<1:
            print("Set of less than 1 somehow exists")
            return 0
        if len(S)==1:
            return dists[S[0]][v]
        else:
            Se=S.copy()
            Se.remove(v)
            #only do the work the subset has never been encountered before
            if str(Se) not in setdex:
                mini=-1
                dex=0
                for i in Se:
                    if i != v:
                        t=heldKarp(Se,i)+dists[i][v]
                        if mini==-1 or t<mini:
                            mini=t
                            dex=i
                setdex[str(Se)]=dex
                return mini
            else:
                return heldKarp(Se,setdex[str(Se)])
    tl=[]
    for i in range(0,len(townL)):
        tl.append(i)
    heldKarp(tl,0)
    #print("tl:"+str(tl))
    #print(setdex)
    tl.remove(0)
    while(len(tl)!=0):
        sol.append(setdex[str(tl)])
        tl.remove(setdex[str(tl)])
    print(sol)
    cutTour(dists,sol,p)                             

