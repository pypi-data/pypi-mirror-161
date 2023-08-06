try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.omfit_ascii import OMFITascii
import numpy as np

__all__ = ['OMFITmmm']


class OMFITmmm(SortedDict, OMFITascii):
    r"""
    OMFIT class used to load from Multi Mode Model output files
    :param filename: filename passed to OMFITascii class
    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()[2:]
        # input
        inUnits = lines[0].split()[1:]
        inVars = lines[1].split()[1:]
        inData = []
        i = 2
        for l in lines[i:]:
            if l[0] == '#':
                break
            i += 1
            inData.append([float(d) for d in l.split()])
        # ouput
        outUnits = lines[i + 1].split()[1:]
        outVars = lines[i + 2].split()[1:]
        outData = []
        for l in lines[i + 3 :]:
            outData.append([float(d) for d in l.split()])
        # save data
        for i in range(len(inVars)):
            self[inVars[i]] = np.transpose(inData)[i]
        for i in range(len(outVars)):
            self[outVars[i]] = np.transpose(outData)[i]
