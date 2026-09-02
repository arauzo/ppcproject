"""
Algorithm to remove the Z Configuration from a prelation table
Corregido para Python 3.14 - TFG Alvaro
"""

def zconf(successors):
    """
    Obtain a new prelation table without Z Configuration adding dummy activities
    successors = {'activity': ['successor1', 'successor2'...}
    
    return subgraph dictionary
    """
    subgraph = {}
    visited1 = []
    visited2 = []
    visited3 = []
    
    # Ordenamos los items para asegurar determinismo en la ejecución
    items = sorted(successors.items())
    
    # Compare each pair of activities
    for act, columns in items:
        for act2, columns2 in items:
            common = set(successors[act]) & set(successors[act2])
            not_common = set(successors[act]) ^ set(successors[act2])
            
            # Insert dummy nodes in common activities if the subgraph is a complete bipartite
            if common and not not_common:
                for act_ in common:
                    dum(act2, act_, subgraph, successors)
                    dum(act, act_, subgraph, successors)
            
            # Insert dummy nodes if prelations have a Z configuration 
            if common and not_common and act != act2 and act not in visited1:
                visited1.append(act2)
                
                for act_ in common:
                    if len(successors[act]) <= len(successors[act2]):
                        dum(act2, act_, subgraph, successors)
                        dum(act, act_, subgraph, successors)
                        
                        if act not in visited3:
                            if len(successors[act]) == len(common) or len(successors[act2]) == len(common):
                                visited3.append(act)
                                
                                for _act in common:
                                    dum(act2, _act, subgraph, successors)
                                    dum(act, _act, subgraph, successors)
                                    
                                for _act in not_common:
                                    dum(act2, _act, subgraph, successors)
                            else:
                                dum(act2, act_, subgraph, successors)
                                for y in not_common:
                                    if y in successors[act]:
                                        dum(act, y, subgraph, successors)
                                        
                    elif len(not_common) != 1:
                        if act2 not in successors[act]: 
                            dum(act, act_, subgraph, successors)
                            for _act in not_common:
                                if _act not in successors[act2]:
                                    dum(act2, act_, subgraph, successors)
                    else: 
                        if act2 not in successors[act] and act not in visited2:
                            visited2.append(act)
                            for _act in common:
                                dum(act2, _act, subgraph, successors)
                                dum(act, _act, subgraph, successors)
                            for _act in not_common:
                                dum(act, _act, subgraph, successors)
    return subgraph

def dum(act, suc, temp, successors):
    """
    Insert a new dummy activity and update the table
    Arreglado: Error de concatenación int + str mediante f-string
    """
    # Usamos f-string para forzar que act y suc sean tratados como texto
    node = f"{act}|{suc}"
   
    if act not in temp:
        temp[act] = list(successors[act])
    
    new_suc = list(temp[act])

    # Definimos la relación de la nueva actividad ficticia
    temp[node] = [str(suc)]
    
    # Añadimos la ficticia a la actividad original y quitamos la relación directa
    new_suc.append(node)
    str_suc = str(suc)
    # Buscamos el sucesor original (puede estar como int o str en la lista)
    if suc in new_suc:
        new_suc.remove(suc)
    elif str_suc in new_suc:
        new_suc.remove(str_suc)
        
    temp[act] = list(set(map(str, new_suc)))
   
    return 0