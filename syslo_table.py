

import namedlist
import graph

def __print_work_table_family(table):
    """
    For debugging purposes, pretty prints Syslo working table
    """
    print "%-5s %-30s %-30s %-15s %-25s %-5s" % ('INDEX', 'Ui', 'Wi', 'STA', 'NON_STA', 'BLOCKED')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %-30s %-15s %-25s %-5s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])



def syslo(temp, grafo):

    Family = namedlist.namedlist('Columns', ['u', 'w', 'est', 'no_est', 'block'])
                            # [0 Activities,   1 Successors, 2 Estable, 3 Non-estable,
                            #   Activities = (Activities with same successors) 
    

       
    #Step 1. Formar familias Ui y Wi
    work_table = {}
    activities = set()
    visited = []
    i = abs(len(grafo) - len(temp))
        
        
    for act, suc in sorted(temp.items()):
        suc = frozenset(suc)
        if act not in activities:
            activities = set(act)
            for act2, suc2 in temp.items():
                if suc == set(suc2) and act != act2 and act2 not in visited:
                    activities.add(act2)
                    visited.append(act)
            
            work_table[i] = Family(list(activities), list(suc), [], [], True)
            i+=1
            
    #print "STEP 2"
    #__print_work_table_family(work_table)



    
    # Step 2. GUARDAR EN CADA COLUMNA LAS ACTIVIDADES ESTABLES Y NO ESTABLES
    visited = []
    visit = []
    group_est = []
    for act, suc in work_table.items():
        visit = []
        
        for q in suc.w:
            for act2, suc2 in work_table.items():
                if act2 > act and q not in visit:
                    if q in suc2.w:
                        #print q, " ES ESTABLE EN", act, 
                        group_est.append(q)
                        visit.append(q)
        #print group_est
        suc.no_est = group_est
        group_est = []
                     
    for act, suc in work_table.items():
        suc.est = list(set(suc.w) - set(suc.no_est))


    for act, suc in work_table.items():
        for act2, suc2 in work_table.items():
            if set(suc.no_est).issubset(set(suc2.est)) and suc.no_est != suc2.est and len(suc.no_est) > 0:
                #print "---------> ", act, act2, suc.no_est
                suc2.no_est = list(set(suc2.no_est) | set(suc.no_est))
        
    for act, suc in work_table.items():
        suc.est = list(set(suc.w) - set(suc.no_est))
        
        
    print "STEP <<<<<<"
    __print_work_table_family(work_table)




    # ORDENAR

    print "(1) ____________________________________"
    
    ordenado1 = []
    
    for k, v in sorted(work_table.items()):
        for r in v.u:  
            for k2, v2 in sorted(work_table.items()):
                #print k, v2
                if r in v2.w and k2 not in ordenado1:
                    #print "ORDEN: ", k2, "(", v2.u, ") va antes que ", k, v.u
                    ordenado1.append(k2)

    #print ordenado1
    
    print "(2) ____________________________________"
    
    ordenado2 = []
    
    for k, v in sorted(work_table.items()):
        for r in v.est:
          for k2, v2 in sorted(work_table.items()):
              if k != k2:
                  if r in v2.w and k2 not in ordenado2:
                     #print "ORDEN: ", k2, "(", v2.u, ") va antes que ", k , v.u
                     ordenado2.append(k2)
    
    #print ordenado2
    
    print "(3) ____________________________________"
    
    ordenado3 = []
    
    for k, v in sorted(work_table.items()):
        for k2, v2 in sorted(work_table.items()):
            if k != k2:
                if set(v.w).issubset(set(v2.w)) and k2 not in ordenado3:
                    #print "ORDEN: ", k2, "(", v.u, ") va antes que ", k 
                    ordenado3.append(k2)
    
    for k, v in sorted(work_table.items()):
        if k not in ordenado3 and k not in ordenado2 and k not in ordenado1:
            ordenado3.append(k)
    
    #print ordenado3
    
    print "------------------------------------"  
    
    
   
    # Step 3 CUBRIR SEGUN REGLAS 3-4-5
    total = []
    x = i + 10
    dang = 0
    if x > 0:
        x += x
    
    for act, suc in sorted(work_table.items()):
        for act2, suc2 in sorted(work_table.items()):
            common = set(suc.no_est) & set(suc2.w)
            if act2 > act and common:
                if set(common).issubset(set(suc.no_est)):
                    for act3, suc3 in sorted(work_table.items()):
                        if act2 not in total and list(suc3.no_est) == list(set(suc2.w) - common):
                            #print ":::::::::::::::", act, act2, x, set(set(suc.w) & set(suc2.w)), list(set(suc.est)), suc3.w
                            if suc.no_est == list(set(suc.w) & set(suc2.w)):
                                if suc3.w == list(set(suc.w) & set(suc2.w)):
                                    dang = x
                            if dang != x:        
                                suc2.u  =  set(suc2.u) | set(list(['z' + str(x)]))
                                suc.w  =  list((set(suc.w) - common) | set(list(['z' + str(x)])))    
                                suc.no_est = list(set(suc.no_est) - set(suc2.w))
                                x+=1
                                #print act2, list(set(predecessors.no_est) - set(set(predecessors2.w) & set(predecessors2.w)))
                                total.append(act2)
                            
                            
                    mico = common
                    for act4, suc4 in sorted(work_table.items()):
                        if act4 > act2 and set(suc4.w) & set(suc2.no_est):
                            common2 = (set(suc4.w) | set(suc2.w)) & set(suc.no_est)
                            if common2:
                                if len(common2) > len(mico):
                                    #print ":::::::::::::::", act, act2, x, set(set(suc.w) & set(suc2.w)), list(set(suc.est))
                                    suc4.u  =  set(suc4.u) | set(list(['z' + str(x)]))
                                    suc.w  =  list((set(suc.w) - common2) | set(list(['z' + str(x)])))    
                                    suc.no_est = list(set(suc.no_est) - set(set(suc2.w) & set(suc4.w)))
                                    
                                    mico = common2
                                    x+=1

    print "STEP 3"
    __print_work_table_family(work_table)

    # Step 4. CUBRIR SEGUN REGLAS 3-4-7
    rule7 = set()
    sei = set()
    dum = []
    ter = []
    p=x
    fin = 0
    for act, suc in sorted(work_table.items()):
        estable = frozenset(suc.no_est)
        if len(activities) != len(temp):
            if set(suc.no_est) == set(estable) and len(estable) > 0:
                dum = work_table[act2].no_est
                rule7.add(act)
                fin +=1
                sei = sei | rule7
                resto = (set(work_table[act].w) - set(dum)) | set(list(['z' + str(x)]))
                common = set(work_table[act].no_est) & set(work_table[act2].no_est)
                #print "________________________", x
                if len(common) == 0:
                    work_table[act].w = list((set(work_table[act].w) - set(work_table[act].no_est)) | set(list(['z' + str(x)]))) 
                else:
                    work_table[act].w = list(resto)
               
                ter.append('z' + str(p))
                p += 1
                work_table[i] = Family(None, None, None, [], True)
                work_table[i].u = ter
                work_table[i].w = work_table[act].no_est
                work_table[i].est = dum
                x+=1
                
    print "STEP 4"
    __print_work_table_family(work_table)

    # Step 5. 
    grafo = {}
    for act, suc in sorted(work_table.items()):
        for e in suc.u:
            grafo[e] = suc.w
    
    return grafo



