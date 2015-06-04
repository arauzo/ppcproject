
import namedlist



def __print_work_table_family(table):
    """
    For debugging purposes, pretty prints Syslo working table
    """
    print "%-5s %-30s %-30s %-15s %-25s %-5s %-10s" % ('INDEX', 'Ui', 'Wi', 'STA', 'NON_STA', 'BLOCKED', 'COVERED')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %-30s %-15s %-25s %-5s %-10s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])



def syslo(temp, grafo):

    Family = namedlist.namedlist('Columns', ['u', 'w', 'est', 'no_est', 'block', 'co'])
                            # [0 Activities,   1 Successors, 2 Estable, 3 Non-estable,
                            #   Activities = (Activities with same successors) 
    

    #Step 0. Rellenar tabla temporal
    work_table = {}
    
    for act, suc in sorted(temp.items()):
        work_table[act] = Family(act, suc, [], [], True, [])

    
    # Step 1. ORDENAR TOPOLOGICAMENTE LAS PRELACIONES
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


    # GUARDAR EN UNA TABLA LAS PRELACIONES ORDENADAS Y AGRUPADAS SI TIENEN MISMOS SUCESORES
    work_sorted_table = {}
    #work_temp = {}
    iguales = []
    x = 0
    vir = []
    
    #print lista
    for g in lista:
            iguales = [g]
            for q, c in work_sorted_table.items():
                if c.w == temp[g] and g not in c.u:
                    iguales = c.u
                    iguales.append(g)
            x += 5
            work_sorted_table[x] = Family(iguales, temp[g], [], [], True, [])
            #work_temp[x] = Family(iguales, temp[g], [], [], True, [])


    # ELIMINAR REDUNDANCIA
    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_sorted_table.items():
            if suc.u == suc2.u and act != act2 and act2 not in vir:
                #print "ELIMINAR", act2, act
                del work_sorted_table[act2]
                #del work_temp[act2]
                x += 1
                vir.append(act)
                break
            

    # Step 2. GUARDAR EN CADA COLUMNA LAS ACTIVIDADES ESTABLES Y NO ESTABLES
    est_act(work_sorted_table)

    # Step 3. CUBRIR SEGUN REGLAS 3-4-5
    acu = []
    x = rule04(work_sorted_table, x, acu)

    print "----"
    __print_work_table_family(work_sorted_table)
    raw_input()
    
    # Step 4. CUBRIR SEGUN REGLAS 3-4-7
    rule05(work_sorted_table, x, Family)

    print "----"
    __print_work_table_family(work_sorted_table)
    raw_input()
   
    # Step 5. 
    grafo = {}
    for act, suc in sorted(work_sorted_table.items()):
        for e in suc.u:
            grafo[e] = suc.w
 
    return grafo



def rule04(work_sorted_table, x, acu):  
    mul = []
    #print ""
    #__print_work_table_family(work_sorted_table)
                             
    for act, suc in sorted(work_sorted_table.items()):
        lista = []
        reserva = []
        for act2, suc2 in sorted(work_sorted_table.items()):
            if act2 > act:
                common = set(suc.no_est) & set(suc2.w)
                if len(common) > 0:
                    if set(acu) == set(suc.no_est):
                        break
                    else:
                        suc.co = list(set(suc.co) | common)
                        acu = list(set(acu) | common)
                        if len(acu) > len(reserva):
                            if len(set(suc2.w) - common) > 0:
                                #print "RESTO : ", set(suc2.w) - common, acu, reserva
                                for act3, suc3 in sorted(work_sorted_table.items()):
                                    if act3 > act2:
                                        if set(set(suc2.w) - common).issubset(set(suc3.w)):
                                            lista.append(act2)
                                            reserva = acu
                                        
                            if len(set(suc2.w) - common) == 0:               
                                lista.append(act2)
                                reserva = acu
        if list(common) != mul:
            x += 1

        if set(acu).issubset(suc.no_est): 
            for r in set(lista):
                work_sorted_table[r].u  = set(work_sorted_table[r].u) | set(list(['d' + str(x)]))
                suc.w  = list((set(suc.w) - set(reserva)) | set(list(['d' + str(x)])))    
                suc.no_est = list(set(suc.no_est) - set(reserva))
                x += 1
            
            #print "|-> ", set(list(['d' + str(x)])), act, lista, suc.no_est, common, list(set(suc.no_est) - common), set(suc2.w) - common, list(acu), set(suc.no_est), work_temp[act].no_est
            acu = []
            
    return x
    
    
def rule05(work_sorted_table, x, Family):
    dum = []
   
    for act, suc in sorted(work_sorted_table.items()):
        for act3, suc3 in sorted(work_sorted_table.items()):
            common = set(suc.no_est) & set(suc3.no_est)
            if len(common) > 0:
                #print ">>> ", act, law, common, set(list(['d' + str(x)])), suc.w, estable
                suc.w = list((set(suc.w) - common) | set(list(['d' + str(x)])))
                suc.no_est = list((set(suc.no_est) - common))
                suc.co = list(set(suc.co) | common)
                work_sorted_table[act+1] = Family(list(['d' + str(x)]), list(common), dum, [], True, [])
                x += 1

    
    
def est_act(work_sorted_table):

    for act, suc in work_sorted_table.items():
        visit = []
        group_est = []
        
        for q in suc.w:
            for act2, suc2 in work_sorted_table.items():
                if act2 > act and q in suc2.w and q not in visit:
                    group_est.append(q)
                    visit.append(q)

        suc.no_est = group_est
        #work_temp[act].no_est = group_est

    print ""
    __print_work_table_family(work_sorted_table)
    raw_input()
    
    #
    for act, suc in work_sorted_table.items():
        suc.est = list(set(suc.w) - set(suc.no_est))
        #work_temp[act].est = list(set(suc.w) - set(suc.no_est))
    
    print ""
    __print_work_table_family(work_sorted_table)
    raw_input()
    
    #
    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_sorted_table.items():
            if set(suc.no_est).issubset(set(suc2.est)) and suc.no_est != suc2.est and len(suc.no_est) > 0:
                suc2.no_est = list(set(suc2.no_est) | set(suc.no_est))
                #work_temp[act2].no_est = list(set(suc2.no_est) | set(suc.no_est))
              
    
    #
    for act, suc in work_sorted_table.items():
        suc.est = list(set(suc.w) - set(suc.no_est))
       # work_temp[act].est = list(set(suc.w) - set(suc.no_est))
    
    
    for act, suc in work_sorted_table.items():
        for act2, suc2 in work_sorted_table.items():
            if suc.no_est != None and suc2.est != None and act != act2:
                common = set(suc.no_est) & set(suc2.est)
                if common and common.issubset(set(suc.no_est))  and common != set(suc2.est):
                    #print act, act2, common
                    suc2.no_est = list(set(suc2.no_est) | common)
                    suc2.est = list(set(suc2.est) - common)
                    
                    #work_temp[act2].no_est = list(set(suc2.no_est) | common)
                    #work_temp[act2].est = list(set(suc2.est) - common)
    
    print ""
    __print_work_table_family(work_sorted_table)
    raw_input()
         