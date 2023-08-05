import numpy as np


def importCSV(fname,/,skiprows=0,delimiter=','):
    print("loading %s..."%(fname))
    with open(fname) as f:
        data = np.genfromtxt(f, dtype=np.float, \
                delimiter=delimiter, skip_header=skiprows,\
                missing_values='',filling_values=0.0)
    return data

def exportCSV(fname,data):
    print("saving %s..."%(fname))
    np.savetxt(fname, data, delimiter=",")
