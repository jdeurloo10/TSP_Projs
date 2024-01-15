import csv
import os
import requests
import networkx as nx

#Idea is to use get provincial tours, link them together where they are closest to get good approximation
#Currently results in worse tour than cut MST, so there are likely bugs to iron out
def getTownList(file):
    with open(r'C:/Users/jdeur/OneDrive/Documents/TSP_Projs/EWC_TSP/'+file) as townsf:
        townRead=csv.reader(townsf)
        townL=[]
        count=0
        for f in townRead:
            if count != 0:
                townL.append(f)
            count+=1
        return townL
    
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

Natl=getTownList('EWC_Towns_Driveable.csv')
provs=['BC','AB','SK','MB','ON','QC','ATL']
provTours=[]

#get provincial tours
for i in provs:
    d=r'C:\Users\jdeur\OneDrive\Documents\TSP_Projs\EWC_TSP\\'+i
    #get the first file in directory
    pt=[]
    dl=os.listdir(d)
    print(dl)
    #Add the source and destination of the first file into the tour
    s=dl[0].find('t')
    d=dl[0].find('.')
    pt.append(dl[0][:s])
    pt.append(dl[0][s+2:d])
    #set current to the first destination
    curr=dl[0][s+2:d]
    #exit loop once we get back to the beginning
    begin=dl[0][:s]
    while curr != begin:
        #find the current node as a source
        for j in dl:
            s=j.find('t')
            if s!=-1:
                if curr == j[:s]:
                    d=j.find('.')
                    curr=j[s+2:d]
                    if curr!= pt[0]:
                        pt.append(curr)
                        print('curr='+str(curr))
                        print('begin='+str(begin)+'\n')

    provTours.append(pt)
    #Now convert provincial index to national indexes
    pl=getTownList(i+'_Towns.csv')
    #find a match in the provincial list and the national list
    for j in pl:
        for k in Natl:
            #once the match is found, assign the national index to the provincial index
            if j[0] == k[0]:
                pt[pt.index(str(pl.index(j)))]=Natl.index(k)
    print(pt)
    
#Get the distance matrices
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

req=requests.get('http://router.project-osrm.org/table/v1/driving/'+coords)
if(str(req)=="<Response [200]>"):
    #get the dist
    js=req.json()
    dists=js["durations"]
else:
    print("No functioning connection")

G=nx.Graph()
ext=[]
#now build a national approximation from west to east
for i in provTours:
    if i == provTours[-1]:
        break
    else:
        if i == provTours[0]:
           ext=i 
        nxt=provTours[provTours.index(i)+1]
        mindis=-1
        clospair=[-1,-1]
        #print("ext:"+str(ext))
        #print("i:"+str(i))
        for j in ext:
            for k in nxt:             
            #compare the list contents one province to the next one over
                if mindis==-1 or dists[int(j)][int(k)]<mindis:
                    #print(str(j)+"-"+str(k))
                    mindis=dists[int(j)][int(k)]
                    clospair[0]=j
                    clospair[1]=k
        print("Closest pair:"+str(clospair))
        #G.add_edge(clospair[0],clospair[1],weight=dists[clospair[0]][clospair[1]])
        #now that we have the closest pair, get the indices of before and after
        #maybe just get and store the index values and get the distances later
        #After all, we need to factor in cost of severing a link to make a new one.
        beaf=[[0,0],[0,0]]
        #beaf[0][x] is always i[i.index(clospair[0])-1]
        #beaf[x][0] is always nxt[nxt.index(clospair[1]-1)]

        #DOUBLE CHECK THESE CASES I FEEL SUS ABOUT THEM
        #0,0
        beaf[0][0]=(ext[ext.index(clospair[0])-1],nxt[nxt.index(clospair[1])-1])
        #1,0
        if clospair[0]==ext[-1]:
           #in the case the closest point is the last on the list
            beaf[1][0]=(ext[0],nxt[nxt.index(clospair[1])-1])
        else:
            beaf[1][0]=(ext[ext.index(clospair[0])+1],nxt[nxt.index(clospair[1])-1])
        #0,1 and 1,1
        if clospair[1]==nxt[-1]:
            beaf[0][1]=(ext[ext.index(clospair[0])-1],nxt[0])
            if clospair[0]==ext[-1]:
                beaf[1][1]=(ext[0],nxt[0])
            else:
                beaf[1][1]=(ext[ext.index(clospair[0])+1],nxt[0])
        else:
            beaf[0][1]=(ext[ext.index(clospair[0])-1],nxt[nxt.index(clospair[1])+1])
            if clospair[0]==ext[-1]:
                beaf[1][1]=(ext[0],nxt[nxt.index(clospair[1])+1])
            else:
                beaf[1][1]=(ext[ext.index(clospair[0])+1],nxt[nxt.index(clospair[1])+1])
        #print(beaf)
        m=-1
        s=0
        for j in beaf:
            for k in j:
                #cost is distance between the two points on different loops minus the distance from the repective loop to each closest pair
                t=dists[int(k[0])][int(k[1])]-dists[int(k[0])][int(clospair[0])]-dists[int(k[1])][int(clospair[1])]
                if m==-1 or t<m:
                    m=t
                    s=k
        #print(m)
        #print(s)
        #TO DO Include case handling Lloyd
        if ext == provTours[0]:
            for j in ext:
                if j != ext[0]:
                    G.add_edge(j,ext[ext.index(j)-1],weight=dists[int(j)][int(ext[ext.index(j)-1])])
                if j == i[-1]:
                    G.add_edge(j,ext[0],weight=dists[int(j)][int(i[0])])

        for j in nxt:
            if j != nxt[0]:
                G.add_edge(j,nxt[nxt.index(j)-1],weight=dists[int(j)][int(nxt[nxt.index(j)-1])])
            if j == nxt[-1]:
                G.add_edge(j,nxt[0],weight=dists[int(j)][int(i[0])])
        if clospair[0]!=clospair[1]:
            G.add_edge(clospair[0],clospair[1],weight=dists[clospair[0]][clospair[1]])
        else:
            print("Lloyd case has occured")
        G.add_edge(s[0],s[1],weight=dists[int(s[0])][int(s[1])])
        G.remove_edge(s[0],clospair[0])
        G.remove_edge(s[1],clospair[1])
        flag=False
        for j in G.nodes():
            #print("Node "+str(j)+':'+str(G.degree[j]))
            if G.degree[j] != 2:
                print("Broken at loop including "+provs[provTours.index(i)])
                flag=True
                print(str(clospair[0])+' '+str(clospair[1]))
                print(G.adj[4])
                break
        if flag:
            break
    #get the order again
    #print("Is the network currently a eulerian?")
    #print(nx.is_eulerian(G))
    ext=[u for u,v in nx.eulerian_circuit(G)]
        

#TO DO--Take all of the edges and make a shapefile
t=0

    
for i in G.edges():
    getLeg(dists,coords,"chained",i[0],i[1])
    #print(str(i[0])+"to"+str(i[1]))
    t=t+G[i[0]][i[1]]['weight']
print(str(t)+" seconds")
h=t/3600
d=h/8
print("That would be "+str(h)+" hours and "+str(d)+" days going at 8 hours per day")


                
        
                    




                     
    

