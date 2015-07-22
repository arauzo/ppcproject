
import namedlist


def __print_work_table_family(table):
    """
    For debugging purposes, pretty prints Syslo working table
    """
    print "%-5s %-30s %-30s %-15s %-25s %-5s %-10s" % ('INDEX', 'Ui', 'Wi', 'STA', 'NON_STA', 'BLOCKED', 'COVERED')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %-30s %-15s %-25s %-5s %-10s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])



def syslo(temp, grafo, alt):

    Family = namedlist.namedlist('Columns', ['u', 'w', 'est', 'no_est', 'block', 'co'])
                            # [0 Activities,   1 Successors, 2 Estable, 3 Non-estable,
                            #   Activities = (Activities with same successors) 
    
  
    # Step 0.1. Topological Sorting
    lista = []

    for k, v in sorted(temp.items()):
        lista.append(k)

    for k, v in sorted(temp.items()):
        for k2, v2 in sorted(temp.items()):
            if k != k2 and set(v).issubset(set(v2)):
                lista.remove(k)
                lista.insert(lista.index(k2), k)
                lista.remove(k2)
                lista.insert(lista.index(k), k2)

    #print lista
    #raw_input()
    # Step 0.2. Save Prelations In A Work Table Group By Same Successors
    work_sorted_table = {}
    iguales = []
    s = 0
    vir = []

    for g in lista:
        iguales = [g]
        for q, c in work_sorted_table.items():
            if c.w == temp[g] and g not in c.u:
                iguales = c.u
                iguales.append(g)
        s += 5 # Se incrementa de 5 en 5 para facilitar inserciones posteriores que alteran el orden inicial
        work_sorted_table[s] = Family(iguales, temp[g], [], [], True, [])

    # Eliminar Redundancia
    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_sorted_table.items():
            if suc.u == suc2.u and act != act2 and act2 not in vir:
                del work_sorted_table[act2]
                vir.append(act)
                break
            
    #__print_work_table_family(work_sorted_table)
    #raw_input()
    
    # Step 0.3. Save Stable And Non Stable Activities
    est_act(work_sorted_table, temp, alt)
    
    __print_work_table_family(work_sorted_table)
    raw_input()
    
    # Step 3. Cover With Rules 3-4-5
    x = rule04(work_sorted_table)


    __print_work_table_family(work_sorted_table)
    raw_input()
    
    
    
    # Step 0.4. Cover With Rules 3-4-7
    rule05(work_sorted_table, x, Family, s)
    
    #__print_work_table_family(work_sorted_table)
    #raw_input()
    

    #print "----"
    __print_work_table_family(work_sorted_table)
    raw_input()
   
    # Step 0.5. Save The Prelations In A New Dictionary
    grafo = {}
    for act, suc in sorted(work_sorted_table.items()):
        for e in suc.u:
            grafo[e] = suc.w
 
    return grafo



def rule04(work_sorted_table):  
    x = 0
                        
    for act, suc in sorted(work_sorted_table.items()):
        lista = []
        reserva = []
        acu =  [] 
        for act2, suc2 in sorted(work_sorted_table.items()):
            common = set(suc.no_est) & set(suc2.w)
            if act2 > act and len(common) > 0:
                if set(acu) != set(suc.no_est):
                    suc.co = list(set(suc.co) | common)
                    acu = list(set(acu) | common)
                    if len(acu) > len(reserva):
                        if len(set(suc2.w) - common) > 0:
                            for act3, suc3 in sorted(work_sorted_table.items()):
                                if act3 > act2:
                                    if set(set(suc2.w) - common).issubset(set(suc3.w)):
                                        lista.append(act2)
                                        reserva = acu
                                        
                        if len(set(suc2.w) - common) == 0:               
                            lista.append(act2)
                            reserva = acu
                
        if set(acu).issubset(suc.no_est): 
            acu = []
            for r in set(lista):
                work_sorted_table[r].u  = set(work_sorted_table[r].u) | set(list(['d' + str(x)]))
                suc.w  = list((set(suc.w) - set(reserva)) | set(list(['d' + str(x)])))    
                suc.no_est = list(set(suc.no_est) - set(reserva))
                x += 1
            

    return x
 
   
    
def rule05(work_sorted_table, x, Family, s):
    dum = []
    acc = set()
    maximalset = set()
    seguir = True
    
    while seguir == True:

        for act, suc in sorted(work_sorted_table.items()):
            visited = []
            seguir = False
            s = max(work_sorted_table) 
            for act3, suc3 in sorted(work_sorted_table.items()):
                common = set(suc.no_est) & set(suc3.no_est)
                if common and act not in visited:
                    common =( set(suc.no_est) & set(suc3.no_est)) - acc
                    
                    #print "-------------------------------", act, act3, common, acc
                    #visited.append(act)
                    acc = acc | common
                    
             
                    if len(common) > 0:
                        for act4, suc4 in sorted(work_sorted_table.items()):
                            if common & set(suc4.no_est):
                                common = common & set(suc4.no_est)
                                maximalset.add(act4)
                               
                            if act4 == max(work_sorted_table):
                                for j in maximalset:
                                    s += 5
                                    work_sorted_table[j].w = list((set(work_sorted_table[j].w) - common) | set(list(['d' + str(x)])))
                                    work_sorted_table[j].no_est = list((set(work_sorted_table[j].no_est) - common))
                                    work_sorted_table[j].co = list(set(work_sorted_table[j].co) | common)
                                   
                                    work_sorted_table[s] = Family(list(['d' + str(x)]), list(common), dum, [], True, [])
                                    x += 1
                                    
                                    #print "________________________________", j, act4
                                #print "_-_-_-_-", maximalset, act4, max(work_sorted_table), common
                                maximalset.clear()
                                
                                break
                    else:
                        common =( set(suc.no_est) & set(suc3.no_est))
                        if len(common) > 0:
                            for act4, suc4 in sorted(work_sorted_table.items()):
                                if common & set(suc4.no_est):
                                    common = common & set(suc4.no_est)
                                    maximalset.add(act4)
                                   
                                if act4 == max(work_sorted_table):
                                    for j in maximalset:
                                        s += 5
                                        work_sorted_table[j].w = list((set(work_sorted_table[j].w) - common) | set(list(['d' + str(x)])))
                                        work_sorted_table[j].no_est = list((set(work_sorted_table[j].no_est) - common))
                                        work_sorted_table[j].co = list(set(work_sorted_table[j].co) | common)
                                       
                                        work_sorted_table[s] = Family(list(['d' + str(x)]), list(common), dum, [], True, [])
                                        x += 1
                                        
                                        #print "________________________________", j, act4
                                    #print "_-_-_-_-", maximalset, act4, max(work_sorted_table), common
                                    maximalset.clear()
                                    
                                    break
                        
                        
                        
        for act, suc in work_sorted_table.items():
            if suc.no_est != []:
                seguir = True
                break
            
                
                            

    
def est_act(work_sorted_table, temp, alt):

    
    for act, suc in work_sorted_table.items():
        visit = []
        for q in suc.w:
            ind = set(suc.u).pop()
            if ind not in visit:
                print suc.u, "-",  temp[ind]
                res = []
                for h in temp[ind]:
                    p = 0
                    com = set()
                    print "-", alt[h]
                    visit.append(ind)
            
                    for f in alt[h]:
                        print "-> ", f, temp[f]
                        if p == 0:
                            com = set(temp[f])
                            p = 1
                            res.append(h)
                        else:
                            com = com & set(temp[f])
                            res.append(h)
                        
                        
                        
                    if set(temp[ind]) == com:          
                        print "_________________________", com, h, act, res
                        work_sorted_table[act].est = list(set(work_sorted_table[act].est) | set([h]))
                        
                        work_sorted_table[act].no_est = list(set(suc.w) - set(work_sorted_table[act].est))
        if suc.est == []:
            work_sorted_table[act].no_est = suc.w
