
import namedlist



def syslo(temp, alt):

    Family = namedlist.namedlist('Columns', ['u', 'w', 'est', 'no_est'])
                            # [0 Activities,   1 Successors, 2 Estable, 3 Non-estable,
                            #   Activities = (Activities with same successors) 
    

  
    # Step 0.1. Topological Sorting
    column = []

    for k, v in sorted(temp.items()):
        column.append(k)

    for k, v in sorted(temp.items()):
        for k2, v2 in sorted(temp.items()):
            if k != k2 and set(v).issubset(set(v2)):
                column.remove(k)
                column.insert(column.index(k2), k)
                column.remove(k2)
                column.insert(column.index(k), k2)


    # Step 0.2. Save Prelations In A Work Table Group By Same Successors
    work_sorted_table = {}
    partition = []
    s = 0
    visited = []

    for g in column:
        partition = [g]
        for q, c in work_sorted_table.items():
            if c.w == temp[g] and g not in c.u:
                partition = c.u
                partition.append(g)
        s += 1
        work_sorted_table[s] = Family(partition, temp[g], [], [])

    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_sorted_table.items():
            if suc.u == suc2.u and act != act2 and act2 not in visited:
                del work_sorted_table[act2]
                visited.append(act)
                break
            
            
    # Step 1. Save Stable And Non Stable Activities
    est_act(work_sorted_table, temp, alt)
    
    
    # Step 2. Cover With Rule 5
    x = rule04(work_sorted_table)
    
    
    # Step 3. Cover With Rule 7
    rule05(work_sorted_table, x, Family, s)
    
    for act, suc in work_sorted_table.items():
        for f in suc.u:
            if f not in alt:
                for act2, suc2 in work_sorted_table.items():
                  for t in suc.w:
                      if t in suc2.w and act != act2:
                          work_sorted_table[act].w = list(set(work_sorted_table[act2].w) | set(work_sorted_table[act].w))


    # Step 4. Save The Prelations In A New Dictionary
    grafo = {}
    for act, suc in work_sorted_table.items():
        for e in suc.u:
            grafo[e] = suc.w
  
    return grafo



def rule04(work_sorted_table):  
    x = 0
                        
    for act, suc in work_sorted_table.items():
        covered = []
        maxmatch = []
        acu =  [] 
        left = set()
        maximal = []
        aux = ''
        
        for act2, suc2 in work_sorted_table.items():
            common = set(suc.no_est) & set(suc2.w)
            
            if act2 > act and common and set(acu) != set(suc.no_est):
                acu = list(set(acu) | common)
                left = (left | (set(suc2.w) - common))
                
                if len(acu) > len(maxmatch):
                    if set(suc2.w) - common != set():
                        for act3, suc3 in work_sorted_table.items():
                            common = common | (set(suc.no_est) & set(suc3.w))
                            if left.issubset(suc.w) and left and common == set(suc.no_est):
                                covered.append(act2)
                                maxmatch = acu
                                break
                                    
                    elif set(suc2.w) == common: 
                        covered.append(act2)
                        if not left:
                            maxmatch = acu
                            
                            if len(suc2.w) > len(maximal):
                                if aux in covered:
                                    covered.remove(aux)
                                    
                                aux = act2
                                covered.append(act2)
                                maximal = suc2.w
                                    
                        else:
                            acu = suc2.w
                            maxmatch = suc2.w
                                
                    elif suc2.w == suc.no_est:               
                        covered = [act2]
                        maxmatch = suc2.w
                        acu =  suc2.w
                        break
                
        if set(acu).issubset(suc.no_est): 
            acu = []
            
            for r in set(covered):
                work_sorted_table[r].u  = set(work_sorted_table[r].u) | set(['d|' + str(x)])
                suc.w  = list((set(suc.w) - set(maxmatch)) | set(['d|' + str(x)]))    
                suc.no_est = list(set(suc.no_est) - set(maxmatch))
                x += 1
    return x
 
   
    
def rule05(work_sorted_table, x, Family, s):
    acc = set()
    broke = set()
    covered = True
    s = max(work_sorted_table) + 1 
    
    while covered == True:
        visited = []
        maximalset = set()
        covered = False
        
        for act, suc in work_sorted_table.items():
            
            for act2 in work_sorted_table:
                common = set(work_sorted_table[act].no_est) & set(work_sorted_table[act2].no_est)
                if suc.no_est != []:
                    if not common and act in broke and suc.no_est:
                        acc = work_sorted_table[act].no_est
                        maximalset.add(act)
                    covered = True
                    broke.add(act)
                    
                    if common and act != act2 and act not in visited:
                        if acc == set():
                            acc = common
                            maximalset.add(act)
                            maximalset.add(act2)
                        else:
                            if common == acc:
                                maximalset.add(act2)
                            
                        visited.append(act2)

            for j in maximalset:
                for n in acc:
                    work_sorted_table[j].no_est = list((set(work_sorted_table[j].no_est) - set([n])))
                    work_sorted_table[j].w = list((set(work_sorted_table[j].w) - set([n])) | set(list(['d|' + str(x)])))
                    work_sorted_table[s] = Family(['d|' + str(x)], list([n]), [], [])
                    s += 1
                    x += 1
                
            acc = []
            maximalset.clear()



    
def est_act(work_sorted_table, temp, alt):

    for act, suc in work_sorted_table.items():
        visit = []
        for q in suc.w:
            ind = set(suc.u).pop()
            if ind not in visit:
                for h in temp[ind]:
                    p = False
                    com = set()
                    visit.append(ind)
            
                    for f in alt[h]:
                        if p == False:
                            com = set(temp[f])
                            p = True
                        else:
                            com = com & set(temp[f])

                    if set(temp[ind]) == com or set(temp[ind]) - set(list([h]))  == com:          
                        work_sorted_table[act].est = list(set(work_sorted_table[act].est) | set([h])) 
                        work_sorted_table[act].no_est = list(set(suc.w) - set(work_sorted_table[act].est))

        if suc.est == []:
            work_sorted_table[act].no_est = suc.w
   
