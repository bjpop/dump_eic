#!/usr/bin/env python 

import os
import os.path
from argparse import ArgumentParser
import subprocess

DEFAULT_OUTDIR = 'eic_graphs'
DEFAULT_CASE_EIC_DATADIR = 'case_eic_data'
DEFAULT_CONTROL_EIC_DATADIR = 'control_eic_data'
DEFAULT_MZ_DELTA = 6.0201

def parse_args():
    parser = ArgumentParser(
        description = 'Plot graphs for ion EICs')
    parser.add_argument(
        '--hits', metavar='FILE', type=str, required=True,
        help='FILE containing list of twin ion hits')
    parser.add_argument(
        '--case_data', metavar='FILE', type=str, default=DEFAULT_CASE_EIC_DATADIR,
        help='path to directory containing case eic data')
    parser.add_argument(
        '--control_data', metavar='FILE', type=str, default=DEFAULT_CONTROL_EIC_DATADIR,
        help='path to directory containing control eic data')
    parser.add_argument(
        '--outdir', metavar='PATH', type=str, default=DEFAULT_OUTDIR,
        help='path to directory containing eic graphs')
    parser.add_argument(
        '--mz_delta', metavar='FLOAT', type=float, default=DEFAULT_MZ_DELTA,
        help='m/z difference between heavy and light ion')
    return parser.parse_args()

GNUPLOT_TEMPLATE = \
    "gnuplot -e \"casefile='{}';controlfile='{}';low='{:.3f}';high='{:.3f}'\" plot.gp > {}"

def main():
    args = parse_args()
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    with open(args.hits) as hits_file:
        for count, line in enumerate(hits_file, 1):
            fields = line.split(',')
            time, mass, intensity, score = fields[:4]
            mass_low = float(mass.strip())
            mass_high = mass_low + args.mz_delta
            hit_str = "hit_" + str(count)
            case_filename = os.path.join(args.case_data, hit_str)
            control_filename = os.path.join(args.control_data, hit_str)
            graph_filename = os.path.join(args.outdir, hit_str + '.svg')
            command = GNUPLOT_TEMPLATE.format(case_filename, control_filename, mass_low,
                mass_high, graph_filename)
            subprocess.call(command, shell=True)

if __name__ == '__main__':
    main()
