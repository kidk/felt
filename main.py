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
import platform
import urllib
import zipfile
import stat


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

    # Check if scenario exists
    if not os.path.isfile(args.scenario):
        print("scenario '%s' not found" % args.scenario)
        return

    # Load from file and parse
    with open(args.scenario, 'r') as content_file:
        content = content_file.read()
    scenario = commentjson.loads(content)

    # Load in scenario
    scenario = Scenario(scenario)

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
    felt = Felt(options, scenario)

    # Start worker
    felt.run()


def init(options):
    """Init function.

    Automatic download of browser requirements (slimerjs and phantomjs)
    """

    # Configuration for installation
    operatingsystem = platform.system()

    phantomjs = False
    slimerjs = False

    path_phantomjs = "bin/phantomjs/phantomjs-2.1.1-macosx/bin/phantomjs"
    path_slimerjs = "bin/slimerjs/slimerjs-0.10.2/slimerjs.py"

    download_phantomjs = ""
    if operatingsystem == "Darwin":
        download_phantomjs = "https://bitbucket.org/ariya/" + \
            "phantomjs/downloads/phantomjs-2.1.1-macosx.zip"
    download_slimerjs = "http://download.slimerjs.org/releases/" + \
        "0.10.2/slimerjs-0.10.2.zip"

    if options.getBrowser() == 'phantomjs':
        phantomjs = True
    if options.getBrowser() == 'slimerjs':
        slimerjs = True

    # Check if we have installations available
    if os.path.isfile(path_phantomjs):
        phantomjs = False

    if os.path.isfile(path_slimerjs):
        slimerjs = False

    # PhantomJS
    if phantomjs:
        print "Creating directories"
        if not os.path.exists("bin/"):
            os.makedirs("bin/")
        if phantomjs and not os.path.exists("bin/phantomjs"):
            os.makedirs("bin/phantomjs")

        print "Downloading phantomjs"
        urllib.urlretrieve(download_phantomjs, "bin/phantomjs.zip")

        print "Unzipping phantomjs"
        zip_ref = zipfile.ZipFile("bin/phantomjs.zip", 'r')
        zip_ref.extractall("bin/phantomjs")
        zip_ref.close()

        print "Setting permissions lost from unzip"
        stats = os.stat(path_phantomjs)
        os.chmod(path_phantomjs, stats.st_mode | stat.S_IEXEC)

        print "Cleaning up"
        os.remove("bin/phantomjs.zip")

    # SlimerJS
    if slimerjs:
        print "Creating directories"
        if not os.path.exists("bin/"):
            os.makedirs("bin/")
        if slimerjs and not os.path.exists("bin/slimerjs"):
            os.makedirs("bin/slimerjs")

        print "Downloading slimerjs"
        urllib.urlretrieve(download_slimerjs, "bin/slimerjs.zip")

        print "Unzipping slimerjs"
        zip_ref = zipfile.ZipFile("bin/slimerjs.zip", 'r')
        zip_ref.extractall("bin/slimerjs")
        zip_ref.close()

        print "Setting permissions lost from unzip"
        stats = os.stat(path_slimerjs)
        os.chmod(path_slimerjs, stats.st_mode | stat.S_IEXEC)

        print "Cleaning up"
        os.remove("bin/slimerjs.zip")

    # Set location in options
    options.setBrowserPath('phantomjs', path_phantomjs)
    options.setBrowserPath('slimerjs', path_slimerjs)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
