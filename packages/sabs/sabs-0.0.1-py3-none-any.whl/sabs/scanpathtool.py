from sabs import read, tidy, convert 
from uncertainties import unumpy as unp
import numpy as np
import matplotlib.pyplot as plt
import argparse
import itertools as it


def main() -> None:
    '''This function is called when the script is explicitly executed'''
    # Parse Arguments given by the user
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputfile",    help="Filename of the measurement to be modified")
    parser.add_argument("-o", "--outputfile",   help="Output filename")
    parser.add_argument("-q", "--quiet",        help="Only output errors to stdout", action="store_true")
    args = parser.parse_args()
    run(args.inputfile, args.outputfile, args.quiet)

def run(
        inputfile,
        outputfile = None,
        quiet = False,
        ):
    scans = read(inputfile, quiet)
    plot(scans)




def plot(scans):
    H, T, R, X, U = convert(tidy(scans))#[:,1:1000]
    hlabel = r'$H\,$[Oe]'
    tlabel = r'$T\,$[K]'
    rlabel = r'$\theta\,$[$^\circ$]'
    xlabel = r'$H_x\,$[Oe]'
    ylabel = r'$H_y\,$[Oe]'
    Hx = H * unp.cos(np.pi*R/180)
    Hy = H * unp.sin(np.pi*R/180)
    plt.figure()
    ax = plt.subplot(111, projection = '3d')
    data = unp.nominal_values((Hx, Hy, T))
    data = data.T
    # Remove nans
    data = data[~(np.isnan(data).any(axis=1))]

    # Remove duplicates
    data_mask = np.append([True], np.any(np.diff(data, axis=0), 1))
    data = data[data_mask]

#    x, y, t = data[:-1].T
#    xe, ye, te = (data[1:]-data[:-1]).T
#    t, te = 100*np.array((t, te))
#    ax.quiver(x, y, t, xe, ye, te, normalize=False) 
    x, y, t = data.T
    ax.plot(x, y, t)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(tlabel)
#    ax.set_xlim((-70000,70000))
#    ax.set_ylim((-70000,70000))
#    ax.set_zlim((0,400))
    plt.show()




if __name__=="__main__":
    main()           
