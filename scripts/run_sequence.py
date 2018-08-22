#!/usr/bin/env python

import argparse
import logging
import inspect

from lsst.ts.sequence import BaseSequence, atcs
from lsst.ts.sequence import __version__

__all__ = ["main"]

log = logging.getLogger(__name__)


def create_parser():
    """Create parser
    """
    description = ["This is the main driver script for the LSST OCS scripts."]

    parser = argparse.ArgumentParser(usage="run_sequence.py [options]",
                                     description=" ".join(description),
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("-v", "--verbose", dest="verbose", action='count', default=0,
                        help="Set the verbosity for the console logging.")
    parser.add_argument("-s", "--sequence", dest="sequence", default=None, type=str,
                        help="Specify the name of the sequence.")
    parser.add_argument("-l", "--list", dest="list", action="store_true",
                        help="List available sequences.")

    return parser


def main(args):
    """
    Main method to startup OCS scripts in python.

    :param args:
    :return:
    """

    valid_sequences = {}
    members = inspect.getmembers(atcs)
    for member in members:
        if inspect.isclass(member[1]) and issubclass(member[1], BaseSequence):
            valid_sequences[member[0]] = member[1]

    if args.list:
        log.info("Listing all available scripts.")
        for sequence in valid_sequences:
            log.info('{}'.format(sequence))
        return 0

    if args.sequence not in valid_sequences:
        raise IOError('{} is not a valid sequence.'.format(args.sequence))

    log.info("Running sequence {}".format(args.sequence))

    seq = valid_sequences[args.sequence]()

    seq.configure()

    log.debug('Estimated run time is {}s'.format(seq.run_time()))

    seq.execute()

    log.info('Done')

    return 0


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    main(args)
