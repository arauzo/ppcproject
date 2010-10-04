import os
import sys
import fileFormats
def openProject(filename):
    """
    Open a project file given by filename
    """
    try:
        actividad  = []
        recurso    = []
        asignacion = []
        schedules  = []
        fileFormat = [
            fileFormats.PPCProjectFileFormat(),
            fileFormats.PPCProjectOLDFileFormat(),
            fileFormats.PSPProjectFileFormat(),
        ]

        

        # Tries to load file with formats that match its extension in format order
        data = None
        extension = filename[filename.rfind('.')+1:]

        for format in fileFormat:
            if extension in format.filenameExtensions:
                try:
                    data = format.load(filename)
                    break
                except fileFormats.InvalidFileFormatException:
                    pass

        if not data:
            print 'Can not understand file'
            sys.exit(1)

        actividad, schedules, recurso, asignacion = data
        return data[0]
    except IOError:
        print 'Error reading file:', filename
        sys.exit(1)

def reversedGraph(graph):
    """
    Returns a new directed graph data structure with all arcs
    reversed. Can be used as a table of inputs to nodes instead of
    outputs (following nodes).
    """
    reverted = {}
    for node in graph:
        inputs = []
        for n,out in graph.items():
            if node in out:
                inputs.append(n)
        reverted[node] = inputs
    return reverted
