
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
    

    #Step 0. Rellenar tabla temporal
    work_table = {}
    i = 0
           
    for act, suc in sorted(temp.items()):
        work_table[i] = Family(act, suc, [], [], True)
        i += 1
    
    
    # Step 1. ORDENAR
    lista = []

    for k, v in sorted(temp.items()):
        lista.append(k)
    

    for k, v in sorted(temp.items()):
        for k2, v2 in sorted(temp.items()):
            if k != k2:
                if set(v).issubset(set(v2)):
                    lista.remove(k)
                    lista.insert(lista.index(k2), k)
                    lista.remove(k2)
                    lista.insert(lista.index(k), k2)


    work_sorted_table = {}
    iguales = []
    x = 0
    vir = []
    
    for g in lista:
            iguales = [g]
            for q, c in work_sorted_table.items():
                if c.w == temp[g] and g not in c.u:
                    iguales = c.u
                    iguales.append(g)
            x += 1
            work_sorted_table[x] = Family(iguales, temp[g], None, None, True)

    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_sorted_table.items():
            if suc.u == suc2.u and act != act2 and act2 not in vir:
                #print "ELIMINAR", act2, act
                del work_sorted_table[act2]
                x += 1
                vir.append(act)
                break
            
            
    #print "ORDENADO"
    #__print_work_table_family(work_sorted_table)
    
    
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
        
    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_sorted_table.items():
            if suc.no_est != None and suc2.est != None and act != act2:
                common = set(suc.no_est) & set(suc2.est)
                if common and common == set(suc.no_est) and len(suc2.est) > 1 and common != set(suc2.est):
                    
                    suc2.no_est = list(set(suc2.no_est) | common)
                    suc2.est = list(set(suc2.est) - common)
                 
                 
    # Step 3. CUBRIR SEGUN REGLAS 3-4-5
    x = rule04(work_sorted_table, x)

    #print "STEP 3"
    #__print_work_table_family(work_sorted_table)
    
    
    # Step 4. CUBRIR SEGUN REGLAS 3-4-7
    dum = []
   
    for act, suc in sorted(work_sorted_table.items()):
        estable = frozenset(suc.no_est)
        if set(suc.no_est) == set(estable) and len(estable) > 0 and act2 > act:
            common = set(suc.no_est) & set(estable)
            suc.w = list((set(suc.w) - common) | set(list(['d' + str(x)])))
            suc.no_est = list((set(suc.no_est) - common))
            work_sorted_table[x] = Family(list(['d' + str(x)]), list(common), dum, [], True)
            x += 1

    
    #print "STEP 4"
    #__print_work_table_family(work_sorted_table)
   
    # Step 5. 
    grafo = {}
    for act, suc in sorted(work_sorted_table.items()):
        for e in suc.u:
            grafo[e] = suc.w
 
    return grafo



def rule04(work_sorted_table, x):  
    
    mul = []

    for act, suc in sorted(work_sorted_table.items()):
        lista2 = []
        mil = set(suc.no_est)
        for act2, suc2 in sorted(work_sorted_table.items()):
            common = mil & set(suc2.w)
            if list(common) != mul:
                x += 1
            if act2 > act and common:
                #print act2, suc.no_est, common, list(set(suc.no_est) - common)
                suc2.u  = set(suc2.u) | set(list(['d' + str(x)]))
                suc.w  = list((set(suc.w) - common) | set(list(['d' + str(x)])))    
                suc.no_est = list(set(suc.no_est) - common)
                lista2.append(act2)
                mul = list(common)
                
                if len(list(set(suc.no_est) - common)) > 0 or act2 != max(work_sorted_table):
                    rule04(work_sorted_table, x)
                else:
                    break
                break

    return x