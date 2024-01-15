import csv
import requests
import networkx as nx


#helper get a jsons of a route
def getLeg(dists,coords,fold,s,d):
    rte=''
    with open(r'C:\Users\jdeur\OneDrive\Documents\TSP_Projs\EWC_TSP\\'+fold+'\\'+str(s)+'to'+str(d)+'.txt','w') as edfl:
        rte=requests.get('http://router.project-osrm.org/route/v1/driving/'+townL[s][2]+','+townL[s][3]+';'+townL[d][2]+','+townL[d][3]+'?overview=simplified&geometries=geojson')
        rte=rte.json()
        rte=str(rte["routes"][0]["geometry"])
        rte=rte.replace("'",'"')
        edfl.write(rte)
        edfl.close()
    return

def getTourL(tour,f):
    G=nx.Graph()
    for j in tour:
        if j != tour[0]:
            getLeg(dists,coords,f,j,tour[tour.index(j)-1])
            G.add_edge(j,tour[tour.index(j)-1],weight=dists[j][tour[tour.index(j)-1]])
        if j == tour[-1]:
            getLeg(dists,coords,f,j,tour[0])
            G.add_edge(j,tour[0],weight=dists[j][tour[0]])
    t=0
    for i in G.edges():
        t=t+G[i[0]][i[1]]['weight']
    print(str(t)+" seconds")
    h=t/3600
    d=h/8
    print("That would be "+str(h)+" hours and "+str(d)+" days going at 8 hours per day")
    return

with open(r'C:\Users\jdeur\OneDrive\Documents\TSP_Projs\EWC_TSP\EWC_Towns_Driveable.csv') as townsf:
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

ftry=[0,1,2,3,4,6,7,5,8,9,10,11,12,13,14,15,16,17,19,18,21,22,24,23,25,26,27,28,
      29,30,31,32,33,34,35,36,20,37,38,39,66,40,41,42,43,44,64,45,46,47,48,49,50,
        51,52,53,55,54,65,56,57,58,59,60,61,62,63    
      ]

try22=[61,62,0,63,1,2,3,4,6,5,7,8,9,10,37,11,12,13,14,15,16,17,19,18,21,22,24,23
       ,25,26,27,28,29,30,31,32,33,34,35,36,20,38,39,66,40,41,42,43,44,45,46,47,
       48,49,50,51,52,53,55,54,65,56,57,59,60
       ]
req=requests.get('http://router.project-osrm.org/table/v1/driving/'+coords)
if(str(req)=="<Response [200]>"):
    #get the dist
    js=req.json()
    dists=js["durations"]
else:
    print("failed")

orgl=[i for i in range(len(townL))]
#getTourL(orgl,"deflt")
getTourL(ftry,"first_try")
#getTourL(try22,"Attempt2022")
