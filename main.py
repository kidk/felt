#!/usr/bin/env python

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
    """ The main function parses the command line arguments, reads the input file and starts the
    generator. """

    # Parse arguments
    parser = argparse.ArgumentParser(description='Start workload.')
    parser.add_argument('--debug', action='store_true',
                        help="enable debug information")
    parser.add_argument('--verbose', action='store_true',
                        help="makes generator more verbose")
    parser.add_argument('--threads', type=int, default=5,
                        help="number of threads to run simultaneously")
    parser.add_argument('scenario')
    args = parser.parse_args()

    # Check if PhantomJS is available
    if not os.path.isfile("phantomjs"):
        print "PhantomJS not found"
        return

    # Check and open scenario
    if not os.path.isfile(args.scenario):
        print "scenario '%s' not found" % args.scenario
        return

    with open(args.scenario, 'r') as content_file:
        content = content_file.read()

    scenario = json.loads(content);

    # Run options
    options = {
        'threads': args.threads
    }

    # Output information
    print "################################"
    print "\tFelt (%s)" % __version__
    print "################################"
    print
    print " Scenario:", scenario
    print " Options", options
    print
    print "################################"

    # Start worker
    worker = WebworkerService()
    worker.run(scenario, options)


class WebworkerService:
    def run(self, scenario, options):
        self.threadcount = 0

        # Start new one every minute
        while True:
            self.startRun(scenario, options)

            # Keep track of running threads
            try:
                while True:
                    threadQueue.get(False)

                    self.threadcount -= 1

                    threadQueue.task_done()
            except Empty, e:
                pass

            time.sleep(0.25)

    def startRun(self, scenario, options):
        if (5 > self.threadcount):
            # Start threads
            for x in range(options['threads'] - self.threadcount):
                self.threadcount += 1
                Thread(target=execute, args = (scenario, options, )).start()



def execute(scenario, options):
    command = ['./phantomjs', 'worker.js', json.dumps(scenario), json.dumps(options)];
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        nextline = process.stdout.readline()
        sys.stdout.write(nextline)
        sys.stdout.flush()

        if process.poll() != None:
            threadQueue.put("Something")
            break

    return None

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
