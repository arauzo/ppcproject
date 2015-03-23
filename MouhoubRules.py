"""
MOUHOUB ALGORITHM RULES 
Delete dummy arcs to build a graph with minimum dummy activities 
"""
import graph

def rule_1(successors_copy, complete_bipartite):
    """
    # Rule 1 - For each subgraph with common and not uncommon activities, contract end vertices in one vertex
    """
    visited = []

    for node, arcs in successors_copy.items():
        for node2, arcs2 in successors_copy.items():
            common = set(arcs) & set(arcs2)
            not_common = set(arcs) ^ set(arcs2)
                
            if common and not not_common and node != node2:
                if len(common) > 1 and node not in visited:
                    r1  = set(complete_bipartite[node])
                    for vertex in common:
                        r1.discard(str(node) + '/' + vertex)
                        r1.add(str(node)  + '/' + vertex)
                        complete_bipartite[str(node)  + '/' + vertex] =  [vertex]
                            
                    complete_bipartite[node] = list(r1)
                    complete_bipartite[node2] = list(r1)
                    visited.append(node2)

    remove_leftDummies(complete_bipartite)

    return complete_bipartite
    
    
def rule_2(predecessors, complete_bipartite):
    """
    # Rule 2 - For each subgraph with common and not uncommon activities, contract end vertices in one vertex
    """
    visited = []
    predece = graph.reversed_prelation_table(complete_bipartite)
    
    for node, arcs in predecessors.items():
        for node2, arcs2 in predecessors.items():
            common = set(arcs) & set(arcs2)
            not_common = set(arcs) ^ set(arcs2)
                
            if common and not not_common and node != node2:
                if len(common) > 1 and node not in visited and node2 not in visited:
                    visited.append(node) ; visited.append(node2)
                     
                    for p in predece[node2]:
                         complete_bipartite[p] = [node, node2]
    
                    for vertex in arcs:
                        r2 = set(list(complete_bipartite[vertex]))
                        for q in predece[node]:
                            r2.discard(q)
                        for q in predece[node2]:
                            if vertex in complete_bipartite[vertex]:
                                r2.add(q)
    
                        complete_bipartite[vertex] = list(r2) 
              
    remove_leftDummies(complete_bipartite)

    return complete_bipartite
    

def rule_3(complete_bipartite):
    """
    # Rule 3 - If a vertex x has one predecessor vertex y, then contract both vertices in one vertex and delete the resulting loop
    """
    end = False
    predecessors = graph.successors2precedents(complete_bipartite)

    for node, arcs in predecessors.items():
        if len(arcs) == 1 and str(node).find('/') == -1:
            vertex = set(arcs).pop()

            if str(vertex).find('/') != -1:
                end = True
                reg = str(vertex).partition('/')

                for p in predecessors[reg[2]]:
                    for arc in predecessors[p]:
                        r3 = set(complete_bipartite[arc])
                        r3.discard(node)
                        r3.add(reg[2])
                        r3.discard(vertex)
                        
                        if vertex in complete_bipartite:
                            for x in complete_bipartite[vertex]:
                                 r3.add(x) 
                            complete_bipartite[arc] = list(r3)

    remove_leftDummies(complete_bipartite)

    return end



def rule_4(complete_bipartite):
    """
    # Rule 4 - If a vertex x has one successor vertex y, then contract both vertices in one vertex and delete the resulting loop
    """
    end = False
    predecessors = graph.successors2precedents(complete_bipartite)

    for node, arcs in complete_bipartite.items():
        if len(set(arcs)) == 1 and str(set(arcs)).find('/') != -1 and str(node).find('/') == -1:
            vertex = str(node).partition('/')

            if len(set(complete_bipartite[vertex[0]])) == 1:
                end = True
                r4 = set(arcs).pop()
                for t in predecessors[r4]:
                    complete_bipartite[t] = list(complete_bipartite[r4])
      
    remove_leftDummies(complete_bipartite)
            
    return end


def rule_5_6(sucesores_copy, complete_bipartite):
    """
    # Rule 5 - If the successors of x are a superset of the successors y, then delete common activities and connect with a dummy arc from x to y
    # Rule 6 - If the successors of x are a subset of the successors of y, then delete common activities and connect with a dummy arc from y to x

                                    Rule 5 and rule 6 are simetric
    """
    visited = []
    predecessors = graph.successors2precedents(complete_bipartite)
    
    for node, arcs, in  reversed(sorted(sucesores_copy.items())):
        for node2, arcs2, in sucesores_copy.items():
            if set(arcs2).issuperset(arcs) and node != node2 and len(arcs) > 0  and len(arcs) + 1 == len(arcs2):
                if node2 not in visited and predecessors[node] == predecessors[node2]:
                    common = set(arcs) & set(arcs2)
                    not_common = set(arcs) ^ set(arcs2)
                    if len(common) > 1:
                        vertex = not_common.pop()
                        arc1 = node2 + '/' + vertex
                        arc2 = node2 + '/' + node
                        r5r6 = set()
                        r5r6.add(arc2)
                       
                        if complete_bipartite.has_key(arc1):
                            r5r6.add(arc1)
                        else:
                            r5r6.add(vertex)
                        
                        if complete_bipartite.has_key(arc2):
                            complete_bipartite[arc2] = list(set(complete_bipartite[arc2]))
                        else:
                            complete_bipartite[arc2] = list(set(complete_bipartite[node]))
     
                        if complete_bipartite.has_key(arc2):   
                            complete_bipartite[node2] = list(r5r6) 
 
                        visited.append(node)
                        
    remove_leftDummies(complete_bipartite)
    
    return complete_bipartite
    
    

def remove_leftDummies(complete_bipartite):
    """
    # Remove the left dummies arcs no connected
    """
    predecessors = graph.successors2precedents(complete_bipartite)
    
    for node, arcs in predecessors.items():
        if len(arcs) == 0 and str(node).find('/') != -1:
            del complete_bipartite[node]
    return 
    
    
    
def rule_3_4(complete_bipartite):
    """
    # Repeat rule 3 and rule 4. Return a dictionary with the updated prelations
    """
    loop = True
    while loop != False:
        loop = rule_3(complete_bipartite)
    
    loop = True
    while loop != False:
        loop = rule_4(complete_bipartite)
        
    return complete_bipartite
    
