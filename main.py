#!/usr/bin/env python
"""Main file for starting Felt.

Handles input parsing, checking parameters and starting the workload run.
"""

import argparse
import sys
import os
import commentjson
from models import Scenario, Options
from core import Felt
from init import init

__license__ = "MIT"
__maintainer__ = "Samuel Vandamme"
__email__ = "samuel@sava.be"
__author__ = "Samuel Vandamme"
__credits__ = ["Stijn Polfliet", "Samuel Vandamme", "Hatem Mostafa"]
__version__ = "alpha"


def main(args):
    """Main function.

    The main function parses the command line arguments, reads the input file
    and inits the generator.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description='Start workload.')
    parser.add_argument('--debug', action='store_true',
                        help="enable debug information")
    parser.add_argument('--verbose', action='store_true',
                        help="makes generator more verbose")
    parser.add_argument('--threads', type=int,
                        default=Options.DEFAULT_THREADS,
                        help="number of threads to run simultaneously")
    parser.add_argument('--test', action='store_true',
                        help="run a scenario only once")
    parser.add_argument('--slimerjs', action='store_true',
                        help="use slimerjs instead of phantomjs")
    parser.add_argument('--screenshot', action='store_true',
                        help="provide screenshots after each step")
    parser.add_argument('--user-agent', type=str, dest='userAgent',
                        help="provide a custom User-Agent")
    parser.add_argument('--max-time', type=int,
                        default=Options.DEFAULT_MAXTIME, dest='maxTime',
                        help="provide a maximum runtime")
    parser.add_argument('--init', type=str, default="phantomjs", dest="init",
                        choices=['all', 'phantomjs', 'slimerjs'],
                        help="initiate environment and download browsers")
    parser.add_argument('scenario')
    args = parser.parse_args()

    # Load scenarios from disk
    scenarios = []
    if os.path.isfile(args.scenario):
        scenarios.append(loadScenario(args.scenario))
    elif os.path.isdir(args.scenario):
        for file in os.listdir(args.scenario):
            if file.endswith(".json"):
                scenarios.append(
                    loadScenario(
                        os.path.join(args.scenario, file)
                    )
                )
    else:
        print("scenario '%s' not found" % args.scenario)
        return

    # Parse options
    options = Options()

    # Which browser are we using
    if args.slimerjs:
        options.setBrowser('slimerjs')

    # Threads option
    options.setThreads(args.threads)

    # Test option
    options.setTest(args.test)

    # Output information
    options.setVerbose(args.verbose)

    # Debug mode
    options.setDebug(args.debug)

    # Screenshot mode
    options.setScreenshot(args.screenshot)

    # User agent
    options.setUserAgent(args.userAgent)

    # Create watchdog thread
    options.setMaximumExectionTime(args.maxTime)

    # Initiate environment for work
    init(options)

    # Create new Felt class
    felt = Felt(options, scenarios)

    # Start worker
    felt.run()


def loadScenario(file):
    with open(file, 'r') as content_file:
        content = content_file.read()

    json = commentjson.loads(content)
    return Scenario(json)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
