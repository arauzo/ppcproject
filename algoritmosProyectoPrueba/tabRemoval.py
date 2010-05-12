#! /usr/bin/env python
import sys, os
import string

if (1 < len(sys.argv) <= 3) and os.path.exists(sys.argv[1]):
   filename = sys.argv[1]
   backupFilename = filename+'~'
   if len(sys.argv) == 3: 
      nSpaces = int(sys.argv[2])
   else:
      nSpaces = 4

   # Read file
   fin = open(filename)
   lines = fin.readlines()
   fin.close()

   # Backup file
   if os.path.exists(backupFilename):
      os.remove(backupFilename)
   os.rename(filename, backupFilename)

   # Replaces tabs
   fout = open(filename, 'w')
   for l in lines:
      fout.write( l.replace('\t', ' '*nSpaces) )
   fout.close()   
else:
   print "Syntax:", sys.argv[0], "<filename> [n_of_spaces_per_tab(default=3)]"


