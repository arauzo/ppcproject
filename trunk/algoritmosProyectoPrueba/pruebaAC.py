import os
import sys
import algoritmoConjuntos
prelaciones = {
    'A' : [],
    'B' : [],
    'C' : ['A','B'],
    'D' : ['A'],
    'E' : ['B'],
    'F' : ['A','B'],
    'G' : ['C'],
    'H' : ['D','E'],
    'I' : ['D','E','F'],
    'J' : ['D','E','F'],
    'K' : ['D','F','L'],
    'L' : ['A'],
}

itime=os.times()
for i in range(1000):
    g=algoritmoConjuntos.algoritmoN(prelaciones)
ftime=os.times()
utime = ftime[0] - itime[0]
stime = ftime[1] - itime[1]
total = utime + stime
total1 = ftime[4]-itime[4]

print "utime %.4f, stime %.4f, total %.4f" % (utime, stime, total)
print "total %.4f"%(total1)

