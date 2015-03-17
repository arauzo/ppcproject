"""
MOUHOUB ALGORITHM RULES 
Delete dummy arcs to build a graph with minimum dummy activities 
"""
import graph


def rule_1_2_7(complete_bipartite, successors_copy):
    """
    # Rule 1 - If the subgraph is a complete bipartite, then contract beggining vertices in one vertex
    # Rule 2 - If the subgraph is a complete bipartite, then contract end vertices in one vertex
    # Rule 7 - If the subgraph is a bipartite partial, then delete all its arcs and conect the activities building a star of dummy arcs
    
    Rule 1 and 2 are an special case of rule 7 
    """
    new_suc = set()

    for act, sucesores in successors_copy.items():
        for act2, sucesores2 in successors_copy.items():
            if act in successors_copy and act2 in successors_copy:
                common = set(successors_copy[act]) & set(successors_copy[act2])
                not_common = set(successors_copy[act]) ^ set(successors_copy[act2])

                # Build a star of dummy arcs
                if common and not not_common and act != act2 and len(common) > 1:
                    star1 = act2 + '-' + 'dp0'
                    for l in common:
                        star2 = 'dp0'  + '-' + str(l)
                        old_dum = act + '-' + l
                        complete_bipartite[star2] = [l]
                        new_suc.add(star2)
                        if old_dum in complete_bipartite:
                            del complete_bipartite[old_dum]

                    # Update node connections
                    complete_bipartite[star1] = list(new_suc)
                    complete_bipartite[act2] = [star1]

                    for arc in new_suc: 
                        act_ = str(arc).partition('-')
                        complete_bipartite[arc] = [act_[2]]

            new_suc.clear()

    return complete_bipartite


def rule_3(complete_bipartite):
    """
    # Rule 3 - If a vertex x has one predecessor vertex y, then contract both vertices in one vertex and delete the resulting loop
    """
    end = False
    predecessors = graph.successors2precedents(complete_bipartite)

    for act, pred in predecessors.items():
        if len(pred) == 1 and str(act).find('-') == -1:
            act_ = set(pred).pop()

            if str(act_).find('-') != -1:
                end = True
                reg = str(act_).partition('-')
                del complete_bipartite[act_]

                for pre in predecessors[reg[2]]:
                    for arc in predecessors[pre]:
                        new_suc = set(complete_bipartite[arc])
                        new_suc.discard(act)
                        new_suc.add(reg[2])
                        complete_bipartite[arc] = list(new_suc)

    return end



def rule_4(complete_bipartite):
    """
    # Rule 4 - If a vertex x has one successor vertex y, then contract both vertices in one vertex and delete the resulting loop
    """  
    end = False

    for act, succe in complete_bipartite.items():
        if len(set(succe)) == 1 and str(set(succe)).find('-') != -1 and str(act).find('-') == -1:
            _act = str(act).partition('-')

            if len(set(complete_bipartite[_act[0]])) == 1:
                act_suc = set(succe).pop()
                complete_bipartite[act] = list(complete_bipartite[act_suc])
                del complete_bipartite[act_suc] 
                end = True

    return end


def rule_5_6(complete_bipartite, sucesores_copy):
    """
    # Rule 5 - If the successor activities of x are a superset of the successor activities of y, then delete common activities and connect with a dummy arc from x to y
    # Rule 6 - If the successor activities of x are a subset of the successor activities of y, then delete common activities and connect with a dummy arc from y to x

    Rule 5 and rule 6 are simetric
    """
    ini = False

    for act, sucesores, in  reversed(sorted(sucesores_copy.items())):
        for act2, sucesores2, in sucesores_copy.items():

            if set(sucesores2).issuperset(sucesores) and act != act2 and len(sucesores) > 0  and len(sucesores) + 1 == len(sucesores2):
                common = set(sucesores) & set(sucesores2)
                not_common = set(sucesores) ^ set(sucesores2)

                if len(common) > 1:
                    act_ = not_common.pop()
                    arc1 = act2 + '-' + str(act_)
                    arc2 = act2 + '-' + act

                    new_suc = [arc1, arc2] 

                    if ini == False:
                        complete_bipartite[arc2] = list(set(complete_bipartite[act]))
                        prev_suc = list(new_suc)
                        ini = True
                    else:
                        complete_bipartite[arc2] = prev_suc
                        prev_suc = new_suc

                    for ex in common:
                        del complete_bipartite[act2 + '-' + str(ex)]

                    complete_bipartite[act2] = new_suc
                    complete_bipartite[arc1] = [act_]

    return complete_bipartite
    