#!/usr/bin/env python

from socket import gethostname
import sys
import os
from argparse import ArgumentParser
import logging
import pymzml

PROGRAM_NAME = 'dump_eic'
DEFAULT_MZ_DELTA = 6.0201
DEFAULT_LOG_FILE = 'log.txt'
HALF_TIME_WINDOW = 20.0
MIN_INTENSITY = 1000.0

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

    return parser.parse_args()


# assumes input is not empty, and contains floats
def average(ns):
    return sum(ns) / len(ns)

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

    with open(args.hits) as hits_file:
        for hit_num, line in enumerate(hits_file, 1):
            fields = line.split(',')
            time, mass, intensity, score = fields[:4]
            time = float(time.strip())
            mass = float(mass.strip())
            intensity = float(intensity.strip())
            print("looking for {} {}".format(time, mass))
            time_low = time - HALF_TIME_WINDOW
            time_high = time + HALF_TIME_WINDOW
            first_mass_low = mass - 1.0
            second_mass = mass + DEFAULT_MZ_DELTA
            second_mass_high = second_mass + 1.0
            high_intensity = intensity * 3.0
            with open("results_3d/hit_{}".format(hit_num), "w") as output_file:
                for spectrum in parseMZML(args.mzml):
                    spectrum_time = float(spectrum.time)
                    if time_low <= spectrum_time <= time_high:
                        for index, spectrum_mass in enumerate(spectrum.mzs):
                            if first_mass_low <= spectrum_mass <= second_mass_high:
                                spectrum_intensity = spectrum.intensities[index]
                                if MIN_INTENSITY <= spectrum_intensity <= high_intensity:
                                    output_file.write("{} {} {}\n".
                                        format(spectrum_time, spectrum_mass, spectrum_intensity))
                            elif spectrum_mass > second_mass_high:
                                break
                    if spectrum_time > time_high:
                        break

'''
def lookupMassBin(mass, bins):
    bins = bins[:,[0,2]]  # get start, stop_exl values
    high = len(bins) - 1
    low = 0
    while low <= high:
        mid = (low + high) // 2
        binlow, binhigh = bins[mid]
        if mass < binlow:
            high = mid - 1
        elif mass >= binhigh:
            low = mid + 1
        else:
            return mid
    return None
'''

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
        mzData = [float(x) for x in spectrum.mz]
        intData = [float(x) for x in spectrum.i]
        time = spectrum['scan time']
        yield Spectrum(n, time, mzData, intData)

if __name__ == '__main__':
    main()
