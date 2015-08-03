
import namedlist


def __print_work_table_family(table):
    """
    For debugging purposes, pretty prints Syslo working table
    """
    print "%-5s %-30s %-30s %-15s %-25s" % ('INDEX', 'Ui', 'Wi', 'STA', 'NON_STA')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %-30s %-25s %-25s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])



def syslo(temp, grafo, alt):

    Family = namedlist.namedlist('Columns', ['u', 'w', 'est', 'no_est'])
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
        s += 1
        work_sorted_table[s] = Family(iguales, temp[g], [], [])

    # Eliminar Redundancia
    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_sorted_table.items():
            if suc.u == suc2.u and act != act2 and act2 not in vir:
                del work_sorted_table[act2]
                vir.append(act)
                break
            
            
    # Step 0.3. Save Stable And Non Stable Activities
    est_act(work_sorted_table, temp, alt)
    
    # Step 3. Cover With Rules 3-4-5
    x = rule04(work_sorted_table)
    
    # Step 0.4. Cover With Rules 3-4-7
    rule05(work_sorted_table, x, Family, s)
    
    for act, suc in work_sorted_table.items():
        for f in suc.u:
            if str(f).find('|'):
                for act2, suc2 in work_sorted_table.items():
                  for t in suc.w:
                      if t in suc2.w and act != act2:
                          work_sorted_table[act].w = list(set(work_sorted_table[act2].w) | set(work_sorted_table[act].w))

    # Step 0.5. Save The Prelations In A New Dictionary
    grafo = {}
    for act, suc in sorted(work_sorted_table.items()):
        for e in suc.u:
            grafo[e] = suc.w
  
    return grafo



def rule04(work_sorted_table):  
    x = 0
                        
    for act, suc in work_sorted_table.items():
        lista = []
        reserva = []
        acu =  [] 
        resto = set()
        maxim = []
        temp = ''
        
        for act2, suc2 in work_sorted_table.items():
            common = set(suc.no_est) & set(suc2.w)
            
            if act2 > act and len(common) > 0 and set(acu) != set(suc.no_est):
                acu = list(set(acu) | common)
                resto = (resto | (set(suc2.w) - common))
                
                if len(acu) > len(reserva):
                    if set(suc2.w) - common != set():
                        for act3, suc3 in work_sorted_table.items():
                            common = common | (set(suc.no_est) & set(suc3.w))
                            if resto.issubset(suc.w) and resto and common == set(suc.no_est):
                                lista.append(act2)
                                reserva = acu
                                break
                                    
                    elif set(suc2.w) == common: 
                        lista.append(act2)
                        if not resto:
                            reserva = acu
                            
                            if len(suc2.w) > len(maxim):
                                if temp in lista:
                                    lista.remove(temp)
                                    
                                temp = act2
                                lista.append(act2)
                                maxim = suc2.w
                                    
                        else:
                            acu = suc2.w
                            reserva = suc2.w
                                
                    elif suc2.w == suc.no_est:               
                        lista = [act2]
                        reserva = suc2.w
                        acu =  suc2.w
                        break
                
        if set(acu).issubset(suc.no_est): 
            acu = []
            
            for r in set(lista):
                work_sorted_table[r].u  = set(work_sorted_table[r].u) | set(['d|' + str(x)])
                suc.w  = list((set(suc.w) - set(reserva)) | set(['d|' + str(x)]))    
                suc.no_est = list(set(suc.no_est) - set(reserva))
                x += 1
    return x
 
   
    
def rule05(work_sorted_table, x, Family, s):
    dum = []
    acc = set()
    rompe = set()
    seguir = True
    s = max(work_sorted_table) + 1 
    
    while seguir == True:
        visited = []
        maximalset = set()
        seguir = False
        
        for act, suc in work_sorted_table.items():
            
            for act2 in work_sorted_table:
                common = set(work_sorted_table[act].no_est) & set(work_sorted_table[act2].no_est)
                if suc.no_est != []:
                    if not common and act in list(rompe) and len(suc.no_est) > 0:
                        acc = work_sorted_table[act].no_est
                        maximalset.add(act)
                    seguir = True
                    rompe.add(act)
                    break
                if common and act != act2 and act not in visited:
                    if acc == set():
                        acc = common
                        maximalset.add(act)
                        maximalset.add(act2)
                    else:
                        if common == set(acc):
                            maximalset.add(act2)
                        
                    visited.append(act2)

            for j in maximalset:
                for n in acc:
                    work_sorted_table[j].no_est = list((set(work_sorted_table[j].no_est) - set([n])))
                    work_sorted_table[j].w = list((set(work_sorted_table[j].w) - set([n])) | set(list(['d|' + str(x)])))
                    work_sorted_table[s] = Family(list(['d|' + str(x)]), list([n]), dum, [])
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

        if suc.est == []:
            work_sorted_table[act].no_est = suc.w
   
