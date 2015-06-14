
import namedlist


def __print_work_pol(table):
    """
    For debugging purposes, pretty prints imporper covers working table
    """
    print "%-5s %-30s %30s" % ('i', 'Ui', 'Wi')
    for k, col in sorted(table.items()):
        print "%-5s %-30s %30s" % tuple(
                [str(k)] + [list(col[0])] + [str(col[i]) for i in range(1, len(col))])




def makeCover(prelations, successors):

    #SConstruct improper cover work table
    MinRev = namedlist.namedlist('MinRev', ['u', 'w'])
                            # [0 Identical successors,   1 Identical Predecessors)
    
    work_table_pol = {}
     
    #Group by Identical Successors
    visited_pred = {}
    i = 0
    
    for act, columns in successors.items():
        u = []
        pred = frozenset(columns)
        if pred not in visited_pred:
            visited_pred[pred] = act
            u.append(act)
            for act2, columns2 in successors.items():
                if columns2 == columns:
                    u.append(act2)
                    
        if len(u) > 0:
            work_table_pol[i] = MinRev(set(u), [])
            i+=1
            

    #Group by Identical Predecessors
    visited_pred = {}
    i = 0
    
    for act, columns in prelations.items():
        u = []
        pred = frozenset(columns)
        if pred not in visited_pred:
            visited_pred[pred] = act
            u.append(act)
            for act2, columns2 in prelations.items():
                if columns2 == columns:
                    u.append(act2)
                    
        if len(u) > 0:
            if work_table_pol.has_key(i):
                work_table_pol[i].w = list(set(u))
            else:
                work_table_pol[i] = MinRev([], list(set(u)))
            i+=1

      
    return work_table_pol