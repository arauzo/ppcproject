#!/usr/bin/env python
"""
Template for main programs and modules with test code

This template must be used for all programs written in Python and for almost all 
modules (as modules should have test code). 

The comments, specially those marked with XXX, are supposed to be deleted or replaced with your own comments.

It is inspired in the comments from Guido's article[1]. I have not included Usage exception as OptionParser
has the method .error to return when something is wrong on arguments (note that getopt is deprecated).

[1] http://www.artima.com/weblogs/viewpost.jsp?thread=4829
"""
# Imports from Python standard library

# Imports from other external libraries

# Imports from our libraries

# XXX Here functions and classes...

def main():
    """
    XXX Main program or test code
    """
    # Parse arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='Project file to fill (default: stdin)')
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout,
                        help='Name of file to store new project (default: stdout)')
    parser.add_argument('-d', '--distribution', default='Beta', 
                        choices=['Beta', 'Normal', 'Uniform', 'Triangular'],
                        help='Statistical distribution (default: Beta)')
    parser.add_argument('-k', default=0.2, type=float, 
                        help='Value of constant to generate missing values (default: 0.2)')

    args = parser.parse_args()

    # XXX Place here the code for test or main program
    print 'We will read from', args.infile
    print 'We will write to', args.outfile
    print 'Distribution will be', args.distribution
    print 'and constant', args.k

    # XXX Use return 1 or any non 0 code to finish with error state
    return 0

# If the program is run directly
if __name__ == '__main__': 
    # Imports needed just for main()
    import sys
    import argparse
    # Run
    sys.exit(main())

