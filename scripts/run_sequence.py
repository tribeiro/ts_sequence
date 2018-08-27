#!/usr/bin/env python

import argparse
import logging
import inspect

from lsst.ts.sequence import BaseSequence, atcs
from lsst.ts.sequence.setup import configure_logging, generate_logfile
from lsst.ts.sequence import __version__

__all__ = ["main"]


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
    parser.add_argument("-c", "--console-format", dest="console_format", default=None,
                        help="Override the console format.")
    parser.add_argument("-s", "--script", dest="script", default=None, type=str,
                        help="Specify the name of the sequence.")
    parser.add_argument("-l", "--list", dest="list", action="store_true",
                        help="List available scripts.")
    parser.add_argument("-r", "--request", dest="request", default=None, type=str,
                        help="Send a request to the OCS to run a specific script.")
    parser.add_argument("--config", dest="script_config", default=None, type=str,
                        help="Filename with the configuration parameters for the requested script.")

    return parser


def main(args):
    """
    Main method to startup OCS scripts in python.

    :param args:
    :return:
    """

    logfilename = generate_logfile()
    configure_logging(args, logfilename)

    logger = logging.getLogger("script")
    logger.info("logfile=%s", logfilename)

    valid_sequences = {}
    members = inspect.getmembers(atcs)
    for member in members:
        if inspect.isclass(member[1]) and issubclass(member[1], BaseSequence):
            valid_sequences[member[0]] = member[1]

    if args.list:
        logger.info("Listing all available scripts.")
        for script in valid_sequences:
            logger.info('%s', script)
        return 0

    if args.script is not None and args.request is not None:
        raise IOError('Only one of script or request options can be selected.')
    elif args.script is not None and args.script not in valid_sequences:
        raise IOError('{} is not a valid sequence.'.format(args.script))
    elif args.request is not None and args.request not in valid_sequences:
        raise IOError('{} is not a valid sequence.'.format(args.script))

    script = args.script if args.script is not None else args.request

    seq = valid_sequences[script]()

    seq.configure(script_config=args.script_config)

    logger.info('Estimated run time is %s s', seq.run_time())

    if args.script is not None:

        logger.info("Running script %s", script)
        seq.execute()

    elif args.request is not None:

        logger.info("Requesting script %s", script)
        seq.request()

    logger.info('Done')

    return 0


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    main(args)
