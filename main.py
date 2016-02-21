"""Main file for starting Felt.

Handles input parsing, checking parameters and starting the workload run.
"""

import argparse
import subprocess
import sys
import time
import json
import os.path
from Queue import Queue, Empty
from threading import Thread

__license__ = "MIT"
__maintainer__ = "Samuel Vandamme"
__email__ = "samuel@sava.be"
__author__ = "Samuel Vandamme"
__credits__ = ["Stijn Polfliet", "Samuel Vandamme"]
__version__ = "alpha"

threadQueue = Queue()


def main(args):
    """Main function.

    The main function parses the command line arguments, reads the input file
    and starts the generator.
    """
    # Parse arguments
    options = parse_arguments(args)

    # Load in scenario
    with open(options['scenario'], 'r') as content_file:
        content = content_file.read()
    scenario = json.loads(content)

    # Test option
    if options['test']:
        options['threads'] = 1

    # Output information
    if options['verbose']:
        print "################################"
        print "\tFelt (%s)" % __version__
        print "################################"
        print
        print options
        print
        print "################################"

    # Start worker
    worker = WebworkerService()
    worker.run(scenario, options)


def parse_arguments(args):
    """Parse arguments function.

    Takes input from commandline and returns an options array.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description='Start workload.')
    parser.add_argument('--debug', action='store_true',
                        help="enable debug information")
    parser.add_argument('--verbose', action='store_true',
                        help="makes generator more verbose")
    parser.add_argument('--threads', type=int, default=5,
                        help="number of threads to run simultaneously")
    parser.add_argument('--test', action='store_true',
                        help="run a scenario only once")
    parser.add_argument('--slimerjs', action='store_true',
                        help="use slimerjs instead of phantomjs")
    parser.add_argument('scenario')
    args = parser.parse_args()

    # Which browser are we using
    browser = "phantomjs"
    if args.slimerjs:
        browser = "slimerjs"

    # Check if scenario exists
    if not os.path.isfile(args.scenario):
        print "scenario '%s' not found" % args.scenario
        return

    # Run options
    options = {
        'browser': browser,
        'scenario': args.scenario,
        'threads': args.threads,
        'verbose': args.verbose,
        'debug': args.debug,
        'test': args.test
    }

    return options


def which(program):
    """Which function.

    Used to find the correct location of the browser executable.
    """
    import os

    # Authors: Jay, Harmv
    # http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)

    # Special case if file is in current dir
    if is_exe(fname):
        return "./%s" % program

    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(os.path.expanduser(path), program)
            if is_exe(exe_file):
                return exe_file

    return None


class WebworkerService:
    """WebworkerService class."""

    def run(self, scenario, options):
        """Run function.

        Init run of main workload loop
        """
        self.threadcount = 0
        self.threadstarted = 0
        self.running = True

        # Start new one every minute
        while self.running:
            self.startRun(scenario, options)

            # Keep track of running threads
            try:
                while True:
                    threadQueue.get(False)

                    self.threadcount -= 1

                    threadQueue.task_done()

                    # Test mode
                    if options["test"]:
                        self.running = False

            except Empty:
                pass

            time.sleep(0.25)

    def startRun(self, scenario, options):
        """Initiate run."""
        if (options['threads'] > self.threadcount):
            # Start threads
            for x in range(options['threads'] - self.threadcount):
                self.threadcount += 1
                self.threadstarted += 1
                Thread(
                    target=execute,
                    args=(self.threadstarted, scenario, options, )
                ).start()


def execute(threadId, scenario, options):
    """Execute browser thread with options."""
    command = [
        options['browser'],
        'worker.js',
        str(threadId),
        json.dumps(scenario),
        json.dumps(options)
    ]
    process = subprocess.Popen(
        command,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    # Main loop
    while True:
        nextline = process.stdout.readline()
        sys.stdout.write(nextline)
        sys.stdout.flush()

        if process.poll() is not None:
            threadQueue.put("Something")
            break

    return None

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
