#!/usr/bin/python3 

'''
Since everything is supposed to be a single script I will take care to order everything as neatly as possible.
'''

# Section 0:
# Loading dependencies
#

#  Numpy (read)
import numpy as np
from numpy.typing import *

# UNumpy for conversion into internal datastructure
from uncertainties import unumpy as unp
from uncertainties import ufloat
from copy import deepcopy

# Subclassing ndarray for internal datastructure
class Scan(np.ndarray):
    '''Subclass of the numpy array. Allows to add attributes in attrs.'''
    def __new__(cls, input_array, attrs={}):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.attrs = deepcopy(attrs)
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.attrs = getattr(obj, 'attrs', None)

class Result(np.ndarray):
    '''Subclass of the numpy array. Allows to add attributes in attrs.'''
    def __new__(cls, input_array, function=lambda x:np.nan):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.function = function
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.function = getattr(obj, 'function', None)

# File IO 
import os
import io

# Functional Approach
import functools as ft
import itertools as it

# Argparse (CLI)
import argparse

# Suppress Warnings
import warnings

# Plotting
#import matplotlib
#matplotlib.use('Gtk3Agg')
import matplotlib.pyplot as plt

# Fitting
import scipy.odr as odr

# Section 1:
# Command Line Interface
# 

def main() -> None:
    '''This function is called when the script is explicitly executed'''
    # Parse Arguments given by the user
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sampledata",   help="RAW file of the measurement with sample")
    parser.add_argument("-b", "--background",   help="RAW file of the background")
    parser.add_argument("-o", "--outputfile",   help="Output filename")
    parser.add_argument("-E", "--errors",       
            help="Errors in Output file with +/- instead of separate column.", action="store_true")
    parser.add_argument("-p", "--plot",         help="Output Window with Plots", action="store_true")
    parser.add_argument("-m", "--mode",         help="Mode of the substraction function")
    parser.add_argument("-v", "--verbose",      
            help="Increase output verbosity. Show warnings", action="store_true")
    parser.add_argument("-q", "--quiet",        help="Only output errors to stdout", action="store_true")
    args = parser.parse_args()
    if run(
            sampledata = args.sampledata, 
            background = args.background, 
            outputfile = args.outputfile,
            errors     = args.errors,
            mode       = args.mode,
            makeplot   = args.plot,
            verbose    = args.verbose,
            quiet      = args.quiet
            ):
        parser.print_help()


def run(sampledata: str=None,
        background: str=None,
        outputfile: str=None, 
        errors:     bool=False,
        mode:       str='nearest',
        makeplot:   bool=False,
        verbose:    bool=False, 
        quiet:      bool=False
        ):
    if verbose: 
        print(f"Sampledata {sampledata} Background {background} Outputfile {outputfile}")
    else:
        # Turn off warning except when in verbose mode
        warnings.filterwarnings('ignore')
    if errors:
        separate=False
    else: 
        separate=True
    if sampledata and background:
        if not quiet:
            print('Reading Sampledata')
        sampledata = read(sampledata, quiet=quiet)
        if not quiet:
            print('Reading Background')
        background = read(background, quiet=quiet)
        if mode == 'dirty':
            scans = subtract(sampledata, background, mode='dirty', quiet=quiet)
        else: 
            scans, background = subtract(sampledata, background, mode='nearest', quiet=quiet)
        # Tidy the metadata
        scans = tidy(scans)
        sampledata = tidy(sampledata)
        background = tidy(background)
        result = fit(scans, quiet=quiet)
        if outputfile:
            write(outputfile, result, separate, quiet=quiet)
        if makeplot:
            plot(scans, result, sampledata, background, quiet=quiet)
    else:
        if background:
            if not quiet:
                print('Reading Background')
            scans = read(background, quiet=quiet)
        elif sampledata:
            if not quiet:
                print('Reading Sampledata')
            scans = read(sampledata, quiet=quiet)
        else:
            return 1    # print help
        # Tidy the metadata
        scans = tidy(scans)
        result = fit(scans, quiet=quiet)
        if outputfile:
            write(outputfile, result, separate, quiet=quiet)
        if makeplot:
            plot(scans, result, quiet=quiet)


# Section 2:
# Functions
#
#  Subsection 2.0:
#  Helpers
#  

def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def _h5open(filename):
     hdff = h5py.File(
            filename, 
            'w',
            driver = 'core',
            backing_store = False,
            )
     return hdff

def _progress(i, endi, barchar='#', barlength = 30):
        a = int(barlength*i/endi) + 1
        b = barlength - a
        return a * barchar + b * '-'

def tidy(scans: list[Scan]):
    tidy_fields = ['magnetic_field_[Oe]', 'temperature_[K]', 'rotation_angle_[deg]',
            'magnetic_moment_[emu]', 'given_center_[mm]', 'squid_range']
    def _tidy_scan(scan):
        newattrs = {}
        newattrs[tidy_fields[0]] = ufloat(
                np.mean((
                    scan.attrs['high field (Oe)'],
                    scan.attrs['low field (Oe)'])),
                (2*np.log(2))**(-1/2)*np.std((
                    scan.attrs['high field (Oe)'],
                    scan.attrs['low field (Oe)']))
                )
        newattrs[tidy_fields[1]] = ufloat(
                np.mean((
                    scan.attrs['high temp (K)'],
                    scan.attrs['low temp (K)'])),
                (2*np.log(2))**(-1/2)*np.std((
                    scan.attrs['high temp (K)'],
                    scan.attrs['low temp (K)']))
                )
        newattrs[tidy_fields[2]]  = scan.attrs['rotation angle (deg)']
        newattrs[tidy_fields[-2]] = ufloat(scan.attrs['given center (mm)'], 0)
        newattrs[tidy_fields[-1]] = ufloat(scan.attrs['squid range'], 0)
        scan.attrs = newattrs
        return scan
    if isinstance(scans, Scan):
        scan = deepcopy(scans)
        return _tidy_scan(scan)
    elif isinstance(scans, list):
        scans = deepcopy(scans)
        for scan in scans:
            scan = _tidy_scan(scan)
        return scans
    else:
        raise ValueError('Only Scans can be tidied')

def _mean(xs):
    '''meaning with error'''
    xs = np.array(xs)
    return ufloat(xs.mean(), xs.std())

def _span(a):
    '''Calculate the span of a given array'''
    a = unp.nominal_values(a)
    a = a[np.logical_not(np.isnan(a))]
    a = a/a.mean()
    a = np.sum(np.abs(np.diff(a)))
    return(a)

def _scantype(A: list[np.ndarray]) -> int:
    '''Return the index of the array with the greatest
    span for a list of arrays'''
    S = []
    for a in A:
        S.append(_span(a))
    i = np.idxmax(np.array(S))
    return i

def convert(scans: list[Scan]) ->  np.ndarray:
    '''
    Convert the scans into a 3D manifold described by X,Y,Z coordinates. 
    Mainly for plotting and testing.
    '''
    number_of_scans = len(scans)
    number_of_voltages = np.array([len(scan) + 1 for scan in scans])
    number_of_points = number_of_voltages.sum() - 1
    D = np.ones((2, 5, number_of_points))*np.nan
    D = unp.uarray(*D)
    pos = 0
    for scan in scans:
        scanlength = len(scan)
        scanrange = (pos, pos + scanlength)
        # Leave one nan as padding between scans
        pos += scanlength + 1
        D[0, scanrange[0]:scanrange[1]] = scan.attrs['magnetic_field_[Oe]']
        D[1, scanrange[0]:scanrange[1]] = scan.attrs['temperature_[K]']
        D[2, scanrange[0]:scanrange[1]] = scan.attrs['rotation_angle_[deg]']
        D[3, scanrange[0]:scanrange[1]] = scan["Raw Position (mm)"]
        D[4, scanrange[0]:scanrange[1]] = scan["Raw Voltage (V)"]
    return D

#  Subsection 2.1: 
#  Ingesting of RAW data from files
#


def read(filename: str,
        quiet: bool = False) -> {str: Scan}:
    '''procedural
    1. Check for all relevant files. Since QD only provides some data in the *.dat files 
       and not in the *.rw.dat files it is unfortunately neccesary to also 
       load the *.dat files.
        - get the basename 
        - Does {basename}.rw.dat and {basename}.dat exist?
        - Is it a valid input file?
    2. Extract the data from the inputfile into a Scan object 
    3. Discard the QD fit and the initial scan.
    4. Apply the squid range
    5. Return Scan objects in a dict     
    '''
    encoding = 'utf-8'
    
    # 1. Check wheather the file exists, wheather it contains a [Data] section 
    #    and where the scans start and end. Also save the line containing metadata

    basename = filename.replace('.dat', '').replace('.rw', '')
    rawfilename = f'{basename}.rw.dat'
    datfilename = f'{basename}.dat'
    for filename in [rawfilename, datfilename]:
        if not os.path.exists(filename):
            raise IOError(f'Could not locate "{filename}".')
    

    # Load both files to memory
    with open(rawfilename, 'r') as rawfile:
        rawfile = rawfile.read()
    with open(datfilename, 'r') as datfile:
        datfile = datfile.read()
        
    # Split into lines
    rawlines = rawfile.strip().split('\n')
    datlines = datfile.strip().split('\n')
    
    # Got to start of data section
    rawlines = list(it.dropwhile(lambda line: not '[Data]' in line, rawlines))
    datlines = list(it.dropwhile(lambda line: not '[Data]' in line, datlines))
    
    # Save the column headers
    rawcolumns = rawlines[1].split(',')[:-2]
    datcolumns = datlines[1].split(',')
    datusecols = [
            'Range', 
            'Min. Temperature (K)', 
            'Max. Temperature (K)', 
            'Min. Field (Oe)', 
            'Max. Field (Oe)', 
            'Rotation Angle (deg)',
            ]
    datcolumns = [
            (name, idx) 
            for idx, name in enumerate(datcolumns)
            if name in datusecols
            ]
    datusenames, datuseidxs = map(list, zip(*datcolumns))
    # The arrangement of the columns is not reliable from one *.dat file 
    # to the next
    #
    #  0, Comment                            0, Comment
    #  1, Time Stamp (sec)                   1, Time Stamp (sec)
    #  2, Temperature (K)                    2, Temperature (K)
    #  3, Magnetic Field (Oe)                3, Magnetic Field (Oe)
    # 13, Range                             13, Range
    # 35, Min. Temperature (K)              15, Min. Temperature (K)
    # 36, Max. Temperature (K)              16, Max. Temperature (K)
    # 37, Min. Field (Oe)                   17, Min. Field (Oe)
    # 38, Max. Field (Oe)                   18, Max. Field (Oe)
    # 55, Rotation Angle (deg)              35, Rotation Angle (deg)
    # 57, DC Moment Fixed Ctr (emu)         37, DC Moment Fixed Ctr (emu)
    # 58, DC Moment Err Fixed Ctr (emu)     38, DC Moment Err Fixed Ctr (emu)
    # 59, DC Moment Free Ctr (emu)          39, DC Moment Free Ctr (emu)
    # 60, DC Moment Err Free Ctr (emu)      40, DC Moment Err Free Ctr (emu)
    # 61, DC Fixed Fit                      41, DC Fixed Fit
    # 62, DC Free Fit                       42, DC Free Fit
    # 63, DC Calculated Center (mm)         43, DC Calculated Center (mm)
    # 64, DC Calculated Center Err (mm)     44, DC Calculated Center Err (mm)
    # 65, DC Scan Length (mm)               45, DC Scan Length (mm)
    # 66, DC Scan Time (s)                  46, DC Scan Time (s)
    # 67, DC Number of Points               47, DC Number of Points
    # 68, DC Squid Drift                    48, DC Squid Drift
    # 69, DC Min V (V)                      49, DC Min V (V)
    # 70, DC Max V (V)                      50, DC Max V (V)
    # 71, DC Scans per Measure              51, DC Scans per Measure              

    # Read attrs from *.dat file
    datlines = datlines[2:]
    datattrs = np.genfromtxt(
        io.StringIO('\n'.join(datlines)), 
        comments = '#', 
        delimiter = ',', 
        deletechars = '',
        replace_space = ' ',
        names = datusenames,
        usecols = datuseidxs,
        encoding = encoding,
        )
    
    # Cut [Data] and column header line
    rawlines = rawlines[2:]
    
    # Split scans and attrs
    def _split_attrs_scans(output, line):
        # catch the lines with attributes
        if line[0] == ';':
            output[0].append(line)
            output[1].append([])
        # disregard the QD fit in the file
        elif not ',,,' in line:
            output[1][-1].append(line)
        return output
    attrs, scans = ft.reduce(_split_attrs_scans, rawlines, ([],[]))

    # remove the (preliminary?) scans
    # TODO this might be too simple for scans with multiple repetitions 
    # at a temperature. Needs testing.
    attrs = attrs[1::2]
    scans = scans[1::2]

    # Parse attrs into dictionary
    def _parse_attr(acc, kv):
        # Split key and value around '='
        kv = kv.split('=')
        k = kv[0].strip()
        vu = kv[1].strip() 
        # Split the value around ' ' to get the unit
        if ' ' in vu:
            vu = vu.split(' ')
            k = k + f' ({vu[1]})'
            acc[k] = np.float(vu[0])
        else:
            acc[k] = np.float(vu)
        return acc
    attrs = map(lambda attr:(
        ft.reduce(_parse_attr, attr.split(';')[1:], {})
    ), attrs)

    # Compare attrs to datattrs and transfer rotation angle
    
    attrs = list(attrs)
    for idx, attr in enumerate(attrs):
        if attr['squid range'] != datattrs['Range'][idx]:
            print(f'SQUID range mismatch between *.rw.dat \
                    and *.dat files in scan {idx+1}')
        attr['rotation angle (deg)'] = datattrs['Rotation Angle (deg)'][idx]

    # Parse datas into numpy array
    scans = map(lambda scan: np.genfromtxt(
        io.StringIO('\n'.join(scan)), 
        #skip_header=1, 
        comments = '#', 
        delimiter = ',', 
        deletechars='',
        replace_space=' ',
        names = rawcolumns,
        encoding = encoding,
        ), scans)

    # Glue attrs to scans
    scans = [Scan(scan, attrs=attr) for scan, attr in zip(scans, attrs)]

    # Apply SQUID range
    def _apply_squid_range(acc, scan):
        for field in ['Raw Voltage (V)', 'Processed Voltage (V)', ]:
            scan[field] *= scan.attrs['squid range']
        acc.append(scan)
        return acc
    scans = ft.reduce(_apply_squid_range, scans, [])
#        # 3. Discard the (preliminary?) scan with upward direction
#        idx = np.where(np.diff(scan['Raw Position (mm)']) > 0)[0]
#        if idx.size:
#            continue
#        realscannumber += 1


    if not quiet:
        print(f'\rscan #{len(scans):>4d} ', end='')
        print(f'[{_progress(1, 1)}]', end='')
        print()

    # 5. Return the list of Scans.
    return scans

#  Subsection 2.3: 
#  Subtracting of RAW data
#

def subtract(sampledata: list[Scan], background: list[Scan], mode='nearest'
        , quiet: bool = False) -> list[Scan]:
    '''Subtract the background from sampledata'''
    # Make a new Scanobject for the result
    rscans = []
    def _rscan(sscan, bscan):
        '''Makes a new Scan object, performs the subtraction and 
        merges the attrs of sampledata and background'''
        rscan = deepcopy(sscan)
        # Combine temp and field regions
        for field in ['low temp (K)', 'low field (Oe)']:
            rscan.attrs[field] = min(sscan.attrs[field], bscan.attrs[field])
        for field in ['high temp (K)', 'high field (Oe)']:
            rscan.attrs[field] = max(sscan.attrs[field], bscan.attrs[field])
        # combine rotation angles
        for field in ['rotation angle (deg)',]:
            mean = np.mean((sscan.attrs[field], bscan.attrs[field]))
            std  = np.std((sscan.attrs[field], bscan.attrs[field]))
            rscan.attrs[field] = ufloat(mean, std)
        # Also set avg. temp although it is not used.
        for field in ['avg. temp (K)']:
            rscan.attrs[field] = np.mean([sscan.attrs[field], bscan.attrs[field]])
        # Take the mean of the positions
        for field in ['Raw Position (mm)',]:
            arr = np.array([sscan[field], bscan[field]])
            means = np.mean(arr, axis=0) 
            stds = (2*np.log(2))**(-1/2)*np.std(arr, axis=0)
            rscan[field] = unp.nominal_values(unp.uarray(means, stds))
        for field in ['Raw Voltage (V)', 'Processed Voltage (V)']:
            rscan[field] = np.diff(np.array([bscan[field], sscan[field], ]), axis=0)
        return rscan


    # Dirty mode just blindly broadcasts the arrays together and 
    # throws away any points that are left in the end.
    if mode == 'dirty':
        if not quiet: 
            print('Subtracting (dirty mode)')
        # Get scans
        sscans = sampledata
        bscans = background
        # Equalize number of scans
        mlen = min(len(sscans), len(bscans))
        for scans in (sscans, bscans):
            scans = scans[:mlen]
        # Equalize the length of the scans themselfes
        for sscan, bscan in zip(sscans, bscans):
            mlen = min(len(sscan), len(bscan))
            for scan in (sscan, bscan):
                scan = scan[:mlen]
        # Subtract
        for scannumber, (sscan, bscan) in enumerate(zip(sscans, bscans)):
            scannumber += 1
            rscan = _rscan(sscan, bscan)
            if not quiet: 
                print(f'\rscan #{scannumber:>4d}' + 1*' ', end='')
                print(f'[{_progress(scannumber, len(sscans))}]', end='')
            rscans.append(rscan)
        if not quiet:
            print()
        return rscans

    # Nearest mode determines what kind of scan was performed (MvT, MvH, ...) and 
    # finds the closest background scan regarding the varied observable (T, H, ...) 
    # for each sample scan. 
    # In case the scans have different lengths an error is rasised
    elif mode == 'nearest':
        if not quiet:
            print('Subtracting (nearest mode)')
        # Get scans
        sscans = sampledata
        bscans = background
        # Find out what kind of measurement we are dealing with
        sts = _span([scan.attrs['high temp (K)'] for scan in sscans])
        shs = _span([scan.attrs['high field (Oe)'] for scan in sscans])
        srs = _span([scan.attrs['rotation angle (deg)'] for scan in sscans])
        bts = _span([scan.attrs['high temp (K)'] for scan in bscans])
        bhs = _span([scan.attrs['high field (Oe)'] for scan in bscans])
        brs = _span([scan.attrs['rotation angle (deg)'] for scan in bscans])
        kinds = ['MvT', 'MvH', 'MvA']
        sspans = [sts, shs, srs]
        skind = kinds[sspans.index(max(sspans))]
        bspans = [bts, bhs, brs]
        bkind = kinds[bspans.index(max(bspans))]
        if bkind == skind:
            kind = skind
        else:
            raise ValueError(f'Sampledata is {skind} but Background is {bkind}.')
        # Set the field accordingly
        vob = {
                'MvT': ('low temp (K)', 'high temp (K)'),
                'MvH': ('low field (Oe)', 'high field (Oe)'),
                'MvA': ('rotation angle (deg)', 'rotation angle (deg)')
                }
        vob = vob[kind]
        bvobs = [np.mean((bscan.attrs[vob[0]], bscan.attrs[vob[1]])) for bscan in bscans]
        newbdata = {}
        for i, sscan in enumerate(sscans):
            svob = np.mean((sscan.attrs[vob[0]], sscan.attrs[vob[1]]))
            # Assosciate background to samplescans
            j = np.argmin(np.abs(np.array(bvobs) - svob))
            # Subtract
            rscan = _rscan(sscan, bscans[j])
            if not quiet:
                print(f'\rscan #{i+1:>4d}' + 1*' ', end='')
                print(f'[{_progress(i+1, len(sscans))}]', end='')
            rscans.append(rscan)
            newbdata.append(deepcopy(background[bscans[j]]))
        if not quiet:
            print()
        return rscans, newbdata

def fit(scans: list[Scan], 
        radius = 17.*.5,    # SQUID-VSM
        separation = 8.,    # SQUID-VSM
        conversion = ufloat(-5.491071961832668E-07, 1.1759959225425074E-09), # From test measurement 
        quiet: bool = False) -> Result:
    '''Fits the "mexican hat" dipole response curve to the given data. 
    This relies on the ODRPACK library.'''
    # Headsup
    if not quiet:
        print('Fitting')
    # Define the function
    def _voltage(position, offset, drift, sampleshift, amplitude, radius, separation):
        result = offset + drift * (position - sampleshift)\
                + amplitude*(2 * (radius**2 + (position - sampleshift)**2)**(-3/2)\
                - (radius**2 + (separation + position - sampleshift)**2)**(-3/2)\
                - (radius**2 + (-separation + position - sampleshift)**2)**(-3/2))
        return result
    # Pepare function for fitting with ODRPACK
    B_names = ['offset_[V]', 'drift_[V/mm]', 'sampleshift_[mm]', 'amplitude_[V/mm^3]']
    function = lambda B, x :_voltage(x, B[0], B[1], B[2], B[3], radius, separation)
    # Fit
    # First create the results array to hold the results and input the given parameters
    names = list(scans[0].attrs.keys())
    names += ['magnetic_moment_[emu]',] 
    names += ['chi_squared',] 
    names += B_names[::-1] 
    result = np.full((len(scans)), ufloat(np.nan,np.nan),  
        dtype={
            'names': names,
            'formats': len(names)*[type(ufloat(np.nan,np.nan))]
            }
        )
    for scannumber,scan in enumerate(scans):
        center   = unp.nominal_values(scan.attrs['given_center_[mm]'])
        position = unp.nominal_values(scan["Raw Position (mm)"])
        position = np.array(position)
        voltage  = unp.nominal_values(scan["Raw Voltage (V)"])
        voltage  = np.array(voltage)
        model = odr.Model(function)
        data  = odr.RealData(position, voltage)
        ODR   = odr.ODR(data, model, beta0=[.1,.1,center,2000.], ifixb=[1,1,1,1])
        output= ODR.run()
        popt, perr = output.beta, output.sd_beta
        result[names[-5]][scannumber] = ufloat(output.res_var, 0)
        result[names[-4]][scannumber] = ufloat(popt[3], perr[3]) # offset
        result[names[-3]][scannumber] = ufloat(popt[2], perr[2]) # drift
        result[names[-2]][scannumber] = ufloat(popt[1], perr[1]) # sampleshift
        result[names[-1]][scannumber] = ufloat(popt[0], perr[0]) # amplitude
        result[names[-6]][scannumber] = conversion*result[names[-4]][scannumber]
        for field, value in scan.attrs.items():
            result[field][scannumber]=value
        if not quiet:
            print(f'\rscan #{scannumber+1:>4d}' + 1*' ', end='')
            print(f'[{_progress(scannumber, len(scans))}]', end='')
    if not quiet:
        print()
    result = Result(result, function=function)
    return result

def plot(scans: {str: Scan}, result: Result, 
        sampledata: {str: Scan}=None, 
        background: {str: Scan}=None,
        quiet: bool = False) -> None:
    def _data(scans, scannumber, center=False):
        scan = scans[int(scannumber)]
        position = scan["Raw Position (mm)"]
        if center:
            position = position - scan.attrs['given_center_[mm]']
        position = unp.nominal_values(position)
        position = np.array(position)
        voltage  = unp.nominal_values(scan["Raw Voltage (V)"])
        voltage  = np.array(voltage)
        return (position, voltage)
    def _fit(result, scans, scannumber, center=False, numberofpoints=1000):
        position, voltage = _data(scans, scannumber, center=center)
        # Provide nice smooth graph for the fit
        position = np.linspace(position.min(), position.max(), numberofpoints)
        B_names = ['offset_[V]', 'drift_[V/mm]', 'sampleshift_[mm]', 'amplitude_[V/mm^3]']
        function = result.function
        B = [unp.nominal_values(result[name])[int(scannumber)] for name in B_names]
        voltage = function(B, position)
        return (position, voltage)
    # Set up the figure
    plt.rcParams['toolbar'] = 'None'
    plt.rcParams['axes.formatter.limits'] = (0,4)
    fig = plt.figure('SABS - SQUID Advanced Background Subtraction', 
            figsize=(10,7),
            constrained_layout=True,
            )
    fig.set_constrained_layout_pads(w_pad=0, h_pad=0, )
    gs  = fig.add_gridspec(22, 22,  hspace=0, wspace=0)
    ax1 = fig.add_subplot(gs[1:11, 1:10])
    ax2 = fig.add_subplot(gs[1:11, 11:20], sharey=ax1, sharex=ax1)
    ax2.tick_params('y', labelleft=False, left=False)
    ax4 = fig.add_subplot(gs[11:20, 1:20])
    twax = ax4.twinx()
    sliderax = fig.add_subplot(gs[20, 1:20])
    # Plot the results
    # Extract Data
    h = result['magnetic_field_[Oe]']
    hlabel = r'$H\,$[Oe]'
    t = result['temperature_[K]']
    tlabel = r'$T\,$[K]'
    r = result['rotation_angle_[deg]']
    rlabel = r'$\theta\,$[$^\circ$]'
    a = result['magnetic_moment_[emu]']
    #alabel = r'$M\,$[emu]'
    alabel = r'magnetic moment [emu]'
    H, T, R, X, U = convert(scans)
    # Determine what was stable and what was variied
    spans = list(map(_span, (t, h, r)))
    vidx = spans.index(max(spans))
    if vidx == 0:
        v = t
        V = T
        vlabel = tlabel
        cmap = plt.cm.coolwarm
    elif vidx == 1:
        v = h
        V = H
        vlabel = hlabel
        cmap = plt.cm.viridis
    elif vidx == 2:
        v = r
        V = R
        vlabel = rlabel
        cmap = plt.cm.viridis
    else: ValueError('This should not happen')
    nv = unp.nominal_values(v)
    nV = unp.nominal_values(V)
    # Set some colors and labels
    resultcolor='C2'
    sampledatacolor='C0'
    backgroundcolor='C1'
    fitcolor='k'
    if sampledata and not background:
        label = 'sampledata'
        color = sampledatacolor
    elif background and sampledata:
        label = 'difference'
        color = resultcolor
    else: 
        label = 'data'
        color = sampledatacolor
    # 2D MvV with errorbars
    ax4.plot(*unp.nominal_values((v, a)),
            color=color,
            alpha=1,
            lw=1.5)
    ylim=ax4.get_ylim()
    ax4.errorbar(*unp.nominal_values((v, a)), 
            yerr=unp.std_devs(a), 
            xerr=unp.std_devs(v), 
            color=color,
            alpha=0.5,
            ls='',
            lw=1)
    ax4.set_ylim(ylim)
    ax4.set_xlim(nv.min(),nv.max())
    ax4.set_xlabel(vlabel)
    ax4.set_ylabel(alabel)
    R = result['chi_squared']
    twax.plot(*unp.nominal_values((v, R)),
            color='k',
            lw=.4)
    twax.set_ylabel(r'$\chi^2$')
    twax.set_ylim((0, twax.get_ylim()[1]))
    # Fit quality
    ax1.set_xlabel(r'position [mm]')
    ax1.set_ylabel(r'voltage $\times$ squid range [V]')
    dataline, = ax1.plot(*_data(scans, 0,),
            ls='',
            lw=.5,
            marker='x',
            ms=3,
            color=color,
            label=label
            ) 
    if sampledata:
        sscanline, = ax1.plot(*_data(sampledata, 0,),
                ls='',
                lw=.5,
                marker='x',
                ms=3,
                alpha=.8,
                color=sampledatacolor,
                label='sampledata'
                ) 
    if background:
        bscanline, = ax1.plot(*_data(background, 0,),
                ls='',
                lw=.5,
                marker='x',
                ms=3,
                alpha=.8,
                color=backgroundcolor,
                label='background'
                ) 
    fitline,  = ax1.plot(*_fit(result, scans, 0,),
            ls='-',
            marker='',
            color=fitcolor,
            label='fit'
            ) 
    ax1.axhline(0, color='k', lw=1)
    # All scans
    for scannumber in range(len(scans)):
        ax2.plot(*_data(scans, scannumber), 
                color=cmap(np.abs(nv[scannumber])/np.abs(nv).max()))
    dataline2, = ax2.plot(*_data(scans, 1), color='k') 
    ax2.set_xlabel(r'position [mm]')
    # VLine
    axvline = ax4.axvline(nv[0], color='k')
    # Function for updating 
    def _update(scannumber):
        scannumber -= 1
        data = _data(scans, scannumber,)
        dataline.set_xdata(data[0])
        dataline.set_ydata(data[1])
        if sampledata:
            data = _data(sampledata, scannumber,)
            sscanline.set_xdata(data[0])
            sscanline.set_ydata(data[1])
        if background:
            data = _data(background, scannumber,)
            bscanline.set_xdata(data[0])
            bscanline.set_ydata(data[1])
        fit = _fit(result, scans, scannumber,)
        fitline.set_xdata(fit[0])
        fitline.set_ydata(fit[1])
        data = _data(scans, scannumber)
        dataline2.set_xdata(data[0])
        dataline2.set_ydata(data[1])
        axvline.set_xdata(nv[scannumber])
        fig.canvas.draw_idle()
    # Introduce a slider
    from matplotlib.widgets import Slider
    slider = Slider(
        ax=sliderax,
        label='scan #',
        valmin=1,
        valmax=len(scans),
        valinit=1,
        initcolor='none',
        track_color='none',
        valstep=1,
    )
    slider.on_changed(_update)
    ax1.legend(loc='lower right', frameon=False)
    plt.show()

def write(outfile: str, result: Result, separate=True, 
        quiet: bool = False) -> None:
    '''Write the results to a .csv file'''
    # Headsup
    if not quiet:
        print("Writing")
    # Output with +/- notation
    if not separate:
        with open(outfile, 'w', encoding='utf-8') as of:
            #print('#', end=' ', file=of)
            for name in result.dtype.names:
                print(name, end=',', file=of)
            print('\r', file=of)
            for i in range(len(result)):
                if not quiet:
                    print(f'\rscan #{i+1:>4d}' + 1*' ', end='')
                    print(f'[{_progress(i, len(result))}]', end='')
                print(*result[i], sep=',', file=of)
        if not quiet:
            print()
    # Output with separate column for the std. devs.
    else: 
        with open(outfile, 'w', encoding='utf-8') as of:
            #print('#', end=' ', file=of)
            for name in result.dtype.names:
                print(name, end=',', file=of)
                print('std_dev_' + name, end=',', file=of)
            print('\r', file=of)
            for i in range(len(result)):
                if not quiet:
                    print(f'\rscan #{i+1:>4d}' + 1*' ', end='')
                    print(f'[{_progress(i+1, len(result))}]', end='')
                line = np.array((unp.nominal_values(list(result[i])),
                    unp.std_devs(list(result[i])))).T.flatten()
                print(*line, sep=',', file=of)
        if not quiet:
            print()


if __name__=="__main__":
    main()           
