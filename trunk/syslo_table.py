
import namedlist


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
    

    #Step 1. Rellenar tabla temporal
    work_table = {}
    i = 0
           
    for act, suc in sorted(temp.items()):
        work_table[i] = Family(act, suc, [], [], True)
        i += 1
    
    
    # ORDENAR
    lista = []

    for k, v in sorted(temp.items()):
        lista.append(k)
    
    """
    #print "(1) ____________________________________"
    
    ordenado1 = []
    
    for k, v in sorted(work_table.items()):
        for k2, v2 in sorted(work_table.items()):
            common = set(v.w) & set(v2.u)
            if common:
                #print common, " esta en ", k2
                #print "ORDEN: ",  k, v.w, " va antes que ", k2, "(", v2.w, ") "
                ordenado1.append(k)

    
    #print ordenado1
    
    #print "(2) ____________________________________"
    
    ordenado2 = []
    
    for k, v in sorted(work_table.items()):
        for r in v.est:
          for k2, v2 in sorted(work_table.items()):
              if k != k2:
                  if r in v2.w and k2 not in ordenado2:
                     #print "ORDEN: ", k2, "(", v2.u, ") va antes que ", k , v.u
                     ordenado2.append(k2)
    
    #print ordenado2
    """
    
    #print "(3) ____________________________________"
    
    ordenado3 = []
    
    for k, v in sorted(temp.items()):
        for k2, v2 in sorted(temp.items()):
            if k != k2:
                if set(v).issubset(set(v2)):
                    #print "INTERCAMBIAR: ", k, " por ", k2
                    #print "POS: ", k, " => ", lista.index(k2)
                    #print "POS: ", k2, " => ", lista.index(k)
                    lista.remove(k)
                    
                    lista.insert(lista.index(k2), k)
                    lista.remove(k2)
                    lista.insert(lista.index(k), k2)
                    ordenado3.append(k2)
    
    
    
    print "------------------------------------"  
    
    work_sorted_table = {}
    anterior = []
    iguales = []
    k = abs(len(grafo) - len(temp))
    
    for g in lista:
        if g != '0':
            if temp[g] == anterior:
                iguales.append(g)
            else:
                k += 1
                iguales = [g]
            work_sorted_table[k] = Family(iguales, temp[g], None, None, True)
            anterior = temp[g]
        
        
    print "ORDENADO"
    __print_work_table_family(work_sorted_table)
    
    
    # Step 2. GUARDAR EN CADA COLUMNA LAS ACTIVIDADES ESTABLES Y NO ESTABLES

    for act, suc in work_sorted_table.items():
        visit = []
        group_est = []
        
        for q in suc.w:
            for act2, suc2 in work_sorted_table.items():
                if act2 > act and q in suc2.w and q not in visit:
                    group_est.append(q)
                    visit.append(q)

        suc.no_est = group_est

    
    #
    for act, suc in work_sorted_table.items():
        suc.est = list(set(suc.w) - set(suc.no_est))

    #
    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_table.items():
            if set(suc.no_est).issubset(set(suc2.est)) and suc.no_est != suc2.est and len(suc.no_est) > 0:
                suc2.no_est = list(set(suc2.no_est) | set(suc.no_est))
    
    #
    for act, suc in work_sorted_table.items():
        suc.est = list(set(suc.w) - set(suc.no_est))
        
    print "STEP 2"
    __print_work_table_family(work_sorted_table)
    
    
    
   
    # Step 3 CUBRIR SEGUN REGLAS 3-4-5
    total = []
    x = k
    dang = 0

    
    for act, suc in sorted(work_sorted_table.items()):
        for act2, suc2 in sorted(work_sorted_table.items()):
            common = set(suc.no_est) & set(suc2.w)
            if act2 > act and common and set(common).issubset(set(suc.no_est)):
                
                for act3, suc3 in sorted(work_sorted_table.items()):
                    if act2 not in total and list(suc3.no_est) == list(set(suc2.w) - common):

                          if suc.no_est == list(set(suc.w) & set(suc2.w)) and suc3.w == list(set(suc.w) & set(suc2.w)):
                              dang = x
                              
                          if suc.no_est == list(set(suc.w) & set(suc2.w)):
                              suc2.u  = set(suc2.u) | set(list(['d' + str(x)]))
                              suc.w  = list((set(suc.w) - common) | set(list(['d' + str(x)])))    
                              suc.no_est = list(set(suc.no_est) - set(suc2.w))
                              x+=1
                              break
                          
                          if dang != x:        
                              suc2.u  = set(suc2.u) | set(list(['d' + str(x)]))
                              suc.w  = list((set(suc.w) - common) | set(list(['d' + str(x)])))    
                              suc.no_est = list(set(suc.no_est) - set(suc2.w))
                              x+=1
                              
                              total.append(act2)
 
                mico = common
                
                for act4, suc4 in sorted(work_sorted_table.items()):
                    if act4 > act2 and set(suc4.w) & set(suc2.no_est):
                        common2 = (set(suc4.w) | set(suc2.w)) & set(suc.no_est)
                        if common2 and len(common2) > len(mico):
                            suc4.u  =  set(suc4.u) | set(list(['d' + str(x)]))
                            suc.w  =  list((set(suc.w) - common2) | set(list(['d' + str(x)])))    
                            suc.no_est = list(set(suc.no_est) - set(set(suc2.w) & set(suc4.w)))
                                   
                            mico = common2
                            x+=1

    print "STEP 3"
    __print_work_table_family(work_sorted_table)

    # Step 4. CUBRIR SEGUN REGLAS 3-4-7
    rule7 = set()
    sei = set()
    dum = []
    ter = []
    
    for act, suc in sorted(work_sorted_table.items()):
        for act2, suc2 in sorted(work_sorted_table.items()):
            estable = frozenset(suc.no_est)
            if set(suc.no_est) == set(estable) and len(estable) > 0:
                    dum = work_sorted_table[act2].no_est
                    rule7.add(act)
                    sei = sei | rule7
                    
                    resto = (set(work_sorted_table[act].w) - set(dum)) | set(list(['d' + str(x)]))
                    common = set(work_sorted_table[act].no_est) & set(work_sorted_table[act2].no_est)
                    
                    
                    if len(common) != 0:
                        print "----->", x, common
                        work_sorted_table[act].w = list(resto)
                        work_sorted_table[act].no_est = list(set(work_sorted_table[act].no_est ) - common)
                        
                    ter.append('d' + str(x))
                    work_sorted_table[i] = Family(ter, work_sorted_table[act].no_est, None, dum, True)
                    x+=1
                    
    print "STEP 4"
    __print_work_table_family(work_sorted_table)

    # Step 5. 
    grafo = {}
    for act, suc in sorted(work_sorted_table.items()):
        for e in suc.u:
            grafo[e] = suc.w
    
    return grafo


