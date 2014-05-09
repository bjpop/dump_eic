#!/usr/bin/env python

from socket import gethostname
import sys
import os
import os.path
from argparse import ArgumentParser
import logging
import pymzml

PROGRAM_NAME = 'dump_eic'
DEFAULT_MZ_DELTA = 6.0201
DEFAULT_LOG_FILE = 'log.txt'
HALF_TIME_WINDOW = 20.0

ARRAY_WINDOW = 3 # take the average of 3 values near the hit
ARRAY_HALF_WINDOW = ARRAY_WINDOW // 2

def parse_args():
    'Dump an EIC from an mzML file'

    parser = ArgumentParser(description='Dump an EIC from an mzML file')

    parser.add_argument('--log', metavar='FILENAME', type=str, nargs='?',
        help='log progress in FILENAME, defaults to {}'.
        format(DEFAULT_LOG_FILE), const=DEFAULT_LOG_FILE)

    parser.add_argument('--mzml', metavar='FILENAME', type=str,
        help='mzML file containing mass spec data', required=True)

    parser.add_argument('--hits', metavar='FILENAME', type=str,
        help='CSV file containing list of hits', required=True)

    parser.add_argument('--outdir', metavar='PATH', type=str,
        help='output directory for eic files', required=True)

    return parser.parse_args()


def main():
    '''Entry point for the program.'''
    args = parse_args()
    if args.log:
        logging.basicConfig(filename=args.log,
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S')
    command_line_text = ' '.join([PROGRAM_NAME] + sys.argv[1:])
    working_directory = os.getcwd()
    hostname = gethostname()
    logging.info('{}'.format(PROGRAM_NAME))
    logging.info('hostname: {}'.format(hostname))
    logging.info('working directory: {}'.format(working_directory))
    logging.info('command line: {}'.format(command_line_text))

    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)

    # this could consume lots of memory
    spectra = list(parseMZML(args.mzml))

    with open(args.hits) as hits_file:
        for hit_num, line in enumerate(hits_file, 1):
            if hit_num > 1000:
                return
            output_filename = os.path.join(args.outdir, "hit_{}".format(hit_num))
            with open(output_filename, "w") as output_file:
                fields = line.split(',')
                time, mass, intensity, score = fields[:4]
                time = float(time.strip())
                mass_low = float(mass.strip())
                time_low = time - HALF_TIME_WINDOW
                time_high = time + HALF_TIME_WINDOW
                mass_high = mass_low + DEFAULT_MZ_DELTA
                time_low_index = binary_search(time_low, spectra, lambda s: s.time)
                time_high_index = binary_search(time_high, spectra, lambda s: s.time)
                for spectrum in spectra[time_low_index: time_high_index + 1]:
                    mass_index_low = binary_search(mass_low, spectrum.mzs)
                    mass_index_high = binary_search(mass_high, spectrum.mzs)
                    intensity_low = index_array(mass_index_low, spectrum.intensities)
                    intensity_high = index_array(mass_index_high, spectrum.intensities)
                    found_mass_low = index_array(mass_index_low, spectrum.mzs)
                    found_mass_high = index_array(mass_index_high, spectrum.mzs)
                    output_file.write("{} {} {} {} {}\n".
                        format(spectrum.time, found_mass_low, intensity_low, found_mass_high, intensity_high))
                '''
                for spectrum in parseMZML(args.mzml):
                    spectrum_time = float(spectrum.time)
                    if time_low <= spectrum_time <= time_high:
                        index_low = binary_search(mass_low, spectrum.mzs)
                        index_high = binary_search(mass_high, spectrum.mzs)
                        intensity_low = index_array(index_low, spectrum.intensities)
                        intensity_high = index_array(index_high, spectrum.intensities)
                        found_mass_low = index_array(index_low, spectrum.mzs)
                        found_mass_high = index_array(index_high, spectrum.mzs)
                        output_file.write("{} {} {} {} {}\n".
                            format(spectrum_time, found_mass_low, intensity_low, found_mass_high, intensity_high))
                    if spectrum_time > time_high:
                        break
                '''

def average(ns):
    if ns:
        return sum(ns) / len(ns)
    else:
        return 0

def index_array(index, array):
    if index is not None and 0 <= index < len(array):
        return average(array[index - ARRAY_HALF_WINDOW: index + ARRAY_HALF_WINDOW + 1])
    else:
        return 0

def binary_search(target, values, getter = lambda x: x):
    if not values:
        return None
    else:

        high_index = len(values) - 1
        low_index = 0

        #assert(low_index <= high_index)

        while low_index < high_index:
            mid_index = (low_index + high_index) // 2
            mid_val = getter(values[mid_index])
            if target < mid_val:
                high_index = mid_index - 1
            elif mid_val < target:
                low_index = mid_index + 1
            else:
                assert(mid_val == target)
                return mid_index

        return low_index

class Spectrum(object):
    def __init__(self, id, time, mzs, intensities):
        self.time = time
        self.mzs = mzs
        self.intensities = intensities
        self.id = int(id)
    def lookupMz(self, mz, tolerance):
        for count, x in enumerate(self.mzs):
            if abs(x - mz) <= tolerance:
                return self.intensities[count]
        return None

def parseMZML(filename):
    msrun = pymzml.run.Reader(filename)
    for n, spectrum in enumerate(msrun):
        #mzData = [float(x) for x in spectrum.mz]
        #intData = [float(x) for x in spectrum.i]
        time = spectrum['scan time']
        yield Spectrum(n, time, spectrum.mz, spectrum.i)

if __name__ == '__main__':
    main()
