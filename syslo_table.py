"""


"""

import namedlist


Family = namedlist.namedlist('Columns', ['u', 'w', 'est', 'no_est'])
                            # [0 Activities,   1 Successors, 2 Estable, 3 Non-estable,
                            #   Activities = (Activities with same successors) 
    
  

def syslo(temp, pert_graph, alt):
    """
    
    
    """


    # Step 0.1. Topological Sorting
    setfamily = []

    for k in sorted(temp, key = lambda k: len(temp[k]), reverse = True):
        setfamily.append(k)

    for k, v in temp.items():
        for k2, v2 in temp.items():
            if k != k2 and set(v).issubset(set(v2)) and len(v) < len(v2):
                setfamily.remove(k)
                setfamily.insert(setfamily.index(k2), k)
                setfamily.remove(k2)
                setfamily.insert(setfamily.index(k), k2)
                
                
    # Step 0.2. Save Prelations In A Work Table Group By Same Successors
    work_sorted_table = {}
    imp_cover = []
    s = 0
    visited = []

    for g in setfamily:
        imp_cover = [g]
        for q, c in work_sorted_table.items():
            if c.w == temp[g] and g not in c.u:
                imp_cover = c.u
                imp_cover.append(g)
        s += 1
        work_sorted_table[s] = Family(imp_cover, temp[g], [], [])

    # Eliminar Redundancia
    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_sorted_table.items():
            if suc.u == suc2.u and act != act2 and act2 not in visited:
                del work_sorted_table[act2]
                visited.append(act)
                break
            
            
    # Step 0.3. Save Stable And Non Stable Activities
    stables(work_sorted_table, temp, alt)
    
    
    # Step 3. Cover With Rules 5
    x = minCover(work_sorted_table)
    
    
    # Step 0.4. Cover With Rules 7
    maxCover(work_sorted_table, x, s, temp)
    
    
    #
    for act, suc in work_sorted_table.items():
        for f in suc.u:
            if str(f).find('|'):
                for act2, suc2 in work_sorted_table.items():
                  for t in suc.w:
                      if t in suc2.w and act != act2:
                          work_sorted_table[act].w = list(set(work_sorted_table[act2].w) | set(work_sorted_table[act].w))


    # Step 0.5. Save The Prelations In A New Dictionary
    pert_graph = {}
    for act, suc in work_sorted_table.items():
        for e in suc.u:
            pert_graph[e] = suc.w
  
    return pert_graph



def minCover(work_sorted_table):  
    """
    
    
    """
    x = 0
                        
    for act, suc in work_sorted_table.items():
        activities = []
        covered = []
        acc =  [] 
        not_covered = set()
       
        for act2, suc2 in work_sorted_table.items():
            common = set(suc.no_est) & set(suc2.w)

            if act2 > act and len(common) > 0:
                if set(suc2.w) == set(suc.no_est):
                    activities = []
                    activities.append(act2)
                    covered = suc2.w
                    break
                
                elif set(acc) != set(suc.no_est):
                    acc = list(set(acc) | common)
                    not_covered = (not_covered | (set(suc2.w) - common))
                    
                    if set(suc2.w) - common != set():
                        if set(suc2.w).issubset(set(suc.no_est)):
                            activities.append(act2)
                            covered = suc2.w
                                
                            #    
                            if not_covered.issubset(suc.w) and not_covered:
                                for act3, suc3 in work_sorted_table.items():
                                    if act3 > act2:
                                        common = common | (set(suc.no_est) & set(suc3.w))
                                        if common == set(suc.no_est):
                                            activities.append(act2)
                                            acc = set(acc) | set(acc)
                                            covered = set(covered) | set(acc)
                                            break
                 
                    elif set(suc2.w) == common: 
                        activities.append(act2)
                            
                        if not not_covered:
                            covered = acc
                        else:
                            acc = suc2.w
                            covered = suc2.w
                                   
                    elif suc2.w == suc.no_est: 
                        activities = [act2]
                        covered = suc2.w
                        acc = suc2.w
                        break
                     
        #      
        if set(acc).issubset(suc.no_est) and activities != []: 
            acc = []
            for r in activities:
                work_sorted_table[r].u  = set(work_sorted_table[r].u) | set(['d|' + str(x)])
                suc.w  = list((set(suc.w) - set(covered)) | set(['d|' + str(x)]))    
                suc.no_est = list(set(suc.no_est) - set(covered))
                x += 1
    return x
   
    
def maxCover(work_sorted_table, x, s, temp):
    """
    
    
    """
    end_cover = True
    s = max(work_sorted_table) + 1 
    
    while end_cover == True:
        visited = []
        visited2 = []
        maximalset = set()
        end_cover = False
        
        for act, suc in work_sorted_table.items():
            t = False
            acc = set()
            if act in temp:
                for act2, suc2 in work_sorted_table.items():
                    if suc.no_est != [] and act not in visited2:
                        end_cover = True
                        common = set(work_sorted_table[act].no_est) & set(work_sorted_table[act2].no_est)
                        if not common  and len(suc.no_est) > 0:
                            acc = work_sorted_table[act].no_est
                            maximalset.add(act)
                            
                        elif common and act != act2 and act not in visited:
                            if acc == set():
                                acc = common
                                maximalset.add(act)
                                maximalset.add(act2)   
                            else:
                                
                                for act3, suc3 in work_sorted_table.items():
                                    if act3 != act and act3 != act2:
                                        common2 = set(suc2.no_est) & common
                                        
                                        if set(suc3.no_est) & set(common):
                                            acc = set(suc3.no_est) & common
                                            
                                        elif common2:
                                            acc = set(suc2.no_est) & common
                                            maximalset.clear()
                                            
                                            if set(suc.no_est) == common2:
                                                t = True
                                                break
                                            
                                        t = False
                                        break
                  
                            visited.append(act2)
                            visited2.append(act)
                
    
                for j in maximalset:
                    if maximalset == set([act]):
                        for n in acc:
                            dummy_act(work_sorted_table, j, s, x, [n]) 
                            s += 1
                            x += 1
                            
                    if t == True:
                        dummy_act(work_sorted_table, j, s, x, acc)
                        s += 1
                        x += 1
    
                maximalset.clear()

            for act, suc in work_sorted_table.items():
                for n in suc.no_est:
                    dummy_act(work_sorted_table, act, s, x, [n])
                    s += 1
                    x += 1
            
        else:
            break

    return





def dummy_act(work_sorted_table, j, s, x, acc):
    """
    
    """
    work_sorted_table[j].no_est = list((set(work_sorted_table[j].no_est) - set(acc)))
    work_sorted_table[j].w = list((set(work_sorted_table[j].w) - set(acc)) | set(list(['d|' + str(x)])))
    work_sorted_table[s] = Family(list(['d|' + str(x)]), list(acc), [], [])

    return
    
    
   
   
    
def stables(work_sorted_table, temp, alt):
    """
    
    
    """
    
    for act, suc in work_sorted_table.items():
        visit = []
        for q in suc.w:
            ind = set(suc.u).pop()
            if ind not in visit:
                for h in temp[ind]:
                    p = 0
                    com = set()
                    visit.append(ind)
            
                    for f in alt[h]:
                        if p == 0:
                            com = set(temp[f])
                            p = 1
                        else:
                            com = com & set(temp[f])

                    if set(temp[ind]) == com or set(temp[ind]) - set(list([h]))  == com:          
                        work_sorted_table[act].est = list(set(work_sorted_table[act].est) | set([h])) 
                        work_sorted_table[act].no_est = list(set(suc.w) - set(work_sorted_table[act].est))
        #
        if suc.est == []:
            work_sorted_table[act].no_est = suc.w
   
