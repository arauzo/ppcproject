"""
Create a PERT without Z Configuration from a prelation table

prelations = {'activity': ['predecesor1', 'predecesor2'...}

"""
subgraph = {}

def zconf(successors):
    """
    Obtain a new prelation table without Z CONFIGURATION adding dummy activities
    
    return subgraph PERT dictionary
    """
    
    visited1 = []
    visited2 = []
    visited3 = []
    
    # Compare each pair of activities. If they have common and not common successors or common and not common predecessors
    for act in successors:
        for act2 in successors:
            common = set(successors[act]) & set(successors[act2])
            not_common = set(successors[act]) ^ set(successors[act2])
            
            # Insert dummy nodes in common activities if the subgraph is a complete bipartite
            if common and not not_common:
                for act_ in common:
                    dum(act2, act_, successors)
                    dum(act, act_, successors)
            
            # Insert dummy nodes if prelations have a Z configuartion 
            if common and not_common and act != act2 and act not in visited1:
                visited1.append(act2)
                
                for act_ in common:
                    if len(successors[act]) <= len(successors[act2]):
                        dum(act2, act_, successors)
                        dum(act, act_, successors)
                        
                        if act not in visited3:
                            if len(successors[act]) == len(common) or len(successors[act2]) == len(common):
                                visited3.append(act)
                                
                                for _act in common:
                                    dum(act2, _act, successors)
                                    dum(act, _act, successors)
                                    
                                for _act in not_common:
                                    dum(act2, _act, successors)

                            else:
                                dum(act2, act_, successors)
                                
                                for y in not_common:
                                    if y in successors[act]:
                                        dum(act, y, successors)
      
                    elif len(not_common) != 1:
                        if act2 not in successors[act]: 
                            dum(act, act_, successors)
                            
                            for _act in not_common:
                                if _act not in successors[act2]:
                                    dum(act2, act_, successors)
                    else: 
                        if act2 not in successors[act] and act not in visited2:
                            visited2.append(act)
                                
                            for _act in common:
                                dum(act2, _act, successors)
                                dum(act, _act, successors)
                                    
                            for _act in not_common:
                                dum(act, _act, successors)

    return subgraph
        



def dum(act, suc, successors):
    """
    Insert a new dummy activity and update the prelations in subgraph
    """
    
    node = act + "|" + suc
   
    if not subgraph.has_key(act):
        subgraph[act] = successors[act]
    new_suc = list(subgraph[act])

    subgraph[node] = [suc]
    new_suc.append(node)
                        
    if suc in new_suc:
        new_suc.remove(suc)
    subgraph[act] = list(set(new_suc))
   
    return 0


