#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check if a prelations table (AON graph encoded in a dictionary) has cycles
"""
import graph

def check_cycles(prelations):
    """
    Algorithm based on Kahn 1962 to check if dict has cycles
    http://en.wikipedia.org/wiki/Topological_sorting
    """
    #L ← Empty list that will contain the sorted elements
    #S ← Set of all nodes with no incoming edges
    #while S is non-empty do
    #    remove a node n from S
    #    insert n into L
    #    for each node m with an edge e from n to m do
    #        remove edge e from dict
    #        if m has no other incoming edges then
    #            insert m into S
    #if dict has edges then
    #    output error message (graph has at least one cycle)
    #else 
    #    output message (proposed topologically sorted order: L)

    # Work over a copy to make changes
    check_prelations = dict.copy(prelations) 
    # Set of all nodes with no incoming edges
    no_incoming_edges = graph.begining_activities(check_prelations) 

    while len(no_incoming_edges) > 0:
        # Remove node where a cycle can not arrive as no_incoming_edges
        act = no_incoming_edges.pop()
        # Update no_incoming_edges with the new begining activities
        set_prelations = set(check_prelations[act])
        del check_prelations[act]
        no_incoming_edges.update(graph.begining_activities(check_prelations, set_prelations)) 

    # If graph still has edges
    if check_prelations: 
        return False # at least one cycle
    else: 
        return True  # no cycles


def test():
    """
    A few tests
    """
    prelations = {
        'a' : ['b','c'],
        'b' : ['d'],
        'c' : ['e'],
        'd' : ['e'],
        'e' : [],
    }
    
    simple_cycle = {
        'a' : ['b','c'],
        'b' : ['c','d'],
        'c' : ['e','b'],
        'd' : ['e'],
        'e' : [],
    }
    
    cycle = {
        'a' : ['b'],
        'b' : ['c','d'],
        'c' : ['e'],
        'd' : ['e'],
        'e' : ['f','h'],
        'f' : ['g'],
        'g' : ['h','i'],
        'h' : ['f','i'],
        'i' : [],
    }
    
    two_cycles = {
        'a' : ['b','c'],
        'b' : ['c','d'],
        'c' : ['e'],
        'd' : ['e'],
        'e' : ['d','c'],
    }
    
    small_cycle = {
        'a' : ['b'],
        'b' : ['a'],
    }
    
    dict_list = [
                    ('prelations', prelations),
                    ('small_cycle', small_cycle),
                    ('simple_cycle', simple_cycle),
                    ('cycle', cycle),
                    ('two_cycles', two_cycles),
                ]
    
    for name, dict_i in dict_list:
        print "\n", name
        print dict_i
        print check_cycles(dict_i)
        
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed only here
    import sys
    # Run
    RTN = test()
    sys.exit(RTN)
            
