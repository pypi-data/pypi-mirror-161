# -*- coding: utf-8 -*-
"""
  Read in FDSN StationXML file and check against
  IRIS Validation Rules:
  https://github.com/iris-edu/stationxml-validator/wiki/StationXML-Validation-Rule-List

  Can also be used to run suite of example pass/fail xml files
  designed to test each rule (--run-tests)

:copyright:
    Mike Hagerty (m.hagerty@isti.com), 2020-2022
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)

usage: iris-validator [-h] (--infile INFILE | --run-tests) [-s STATION] [-c CHANNEL] [-n NETWORK] [-l LOCATION] [-def] [-i IGNORE [IGNORE ...]]

required arguments (pick one):
  --infile INFILE       // path-to StationXML file, e.g., --infile=/path/to/foo.xml
  --run-tests           // Run IRIS Validator Test Files

options:
  -h, --help            show this help message and exit
  -s STATION, --station STATION, --sta STATION
                        Specify a station code, wildcards are allowed
  -c CHANNEL, --channel CHANNEL, --cha CHANNEL
                        Specify a channel code, wildcards are allowed
  -n NETWORK, --network NETWORK, --net NETWORK
                        Specify a network code, wildcards are allowed
  -l LOCATION, --location LOCATION, --loc LOCATION
                        Specify a location code, wildcards are allowed
  -def, --seismic-only, --seismic_only
                        Only scan default_seismic_channels in: {[BEHSG][HNL][123ENZ]}
  -i IGNORE [IGNORE ...], --ignore IGNORE [IGNORE ...]
                        Specify list of rule codes to ignore
"""

import os
import re
import sys
import argparse

import logging as logger
logger.basicConfig(level=logger.WARN)

from iris_validator import stationxml_validator
from iris_validator.iris_validate import validate_iris_stationxml_examples_vs_rules

def main():

    fname = 'iris-validator'

    args, kwargs = process_cmd_line(fname)

    if args.run_tests:
        validate_iris_stationxml_examples_vs_rules()
    else:
        validator = stationxml_validator(args.infile, kwargs=kwargs, ignore=args.ignore)
        print(sys.argv)
        validator.validate_inventory()
        print("[SUMMARY]:")

        #print("%7s N_Errors:%d N_Warnings:%d\n" % (' ', len(validator.errors), len(validator.warnings)))
        nw = [x for x in validator.warnings if '[' in x[0] and ']' in x[0]]
        ne = [x for x in validator.errors if '[' in x[0] and ']' in x[0]]
        print("%7s N_Errors:%d N_Warnings:%d\n" % (' ', len(ne), len(nw)))

        print("[ERRORS]:\n")
        for msgs in validator.errors:
            for i, msg in enumerate(msgs):
                if i == 0:
                    print(msg)
                else:
                    print("%7s %s" % (' ', msg))

        if args.dont_warn:
            pass
        else:
            print("\n[WARNINGS]:\n")
            for msgs in validator.warnings:
                for i, msg in enumerate(msgs):
                    if i == 0:
                        print(msg)
                    else:
                        print("%7s %s" % (' ', msg))
    return


def process_cmd_line(fname):

    DEFAULT_SEISMIC_CHANNELS = '[BEHSG][HNL][123ENZ]'

    parser = argparse.ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")

    parser._action_groups.append(optional) # 
    group = required.add_mutually_exclusive_group(required=True)

    #required.add_argument("--infile", type=str, metavar='// path-to StationXML file, e.g., --infile=/path/to/foo.xml',
                          #required=True)
    group.add_argument("--infile", type=str, help='// path-to StationXML file, e.g., --infile=/path/to/foo.xml')
    group.add_argument("--run-tests", action='store_true', help='// Run IRIS Validator Test Files')

    #optional.add_argument("--preferred-eventtime", type=UTCDateTime)

    optional.add_argument("-s","--station","--sta", type=str, help="Specify a station code, wildcards are allowed")
    optional.add_argument("-c","--channel","--cha", type=str, help="Specify a channel code, wildcards are allowed")
    optional.add_argument("-n","--network","--net", type=str, help="Specify a network code, wildcards are allowed")
    optional.add_argument("-l","--location","--loc", type=str, help="Specify a location code, wildcards are allowed")

    optional.add_argument("-def","--seismic-only","--seismic_only", action='store_true',
                          help="Only scan default_seismic_channels in: {%s}" % DEFAULT_SEISMIC_CHANNELS)

    optional.add_argument('-i', '--ignore', nargs='+', default=[], help="Specify list of rule codes to ignore")

    optional.add_argument("-e","--dont-warn","--dont_warn","--errors-only", "--errors_only", action='store_true',
                          help="Only print failed tests that result in ERROR, not WARNING")

    args, unknown = parser.parse_known_args()

    if unknown:
        for k in unknown:
            print("ERROR Unknown arg:%s" % k)
        #print(usage)
        parser.print_help()
        exit(2)

    if args.ignore:
        ignore = []
        for x in args.ignore:
            y = x.split(',')
            for i in range(len(y)):
                #print("y[%d]=%s" % (i, y[i]))
                if len(y[i].strip()) > 0:
                    try:
                        ignore.append(int(y[i]))
                    except ValueError as e:
                        print("Error:%s" % e)
                        print("e.g., --ignore 401,402 or --ignore 401 402")
                        parser.print_help()
                        exit(2)
        args.ignore = ignore

    # possible keyword arguments to use in select
    kwargs = {}
    if args.network:
        kwargs["network"] = args.network
    if args.station:
        kwargs["station"] = args.station
    if args.channel:
        kwargs["channel"] = args.channel
    if args.location:
        kwargs["location"] = args.location

    if args.seismic_only and not args.channel:
        kwargs["channel"] = DEFAULT_SEISMIC_CHANNELS

    # Check that infile exists:
    if args.infile and not os.path.isfile(args.infile):
        print("Unable to read infile=%s --> Exiting!" % args.infile)
        parser.print_help()
        exit(2)

    return args, kwargs


if __name__ == "__main__":
    main()
