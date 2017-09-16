"""Core files for Felt.

Handles browser instances
"""

import os
import sys
import time
from threading import Thread
import json
from multiprocessing import Queue
try:
    from queue import Empty
except ImportError:
    from Queue import Empty
import subprocess

__license__ = "MIT"
__maintainer__ = "Samuel Vandamme"
__email__ = "samuel@sava.be"
__author__ = "Samuel Vandamme"
__credits__ = ["Stijn Polfliet", "Samuel Vandamme", "Hatem Mostafa"]
__version__ = "alpha"


class Felt:
    """Felt class."""

    def __init__(self, options, scenarios):
        """Init vars."""
        self.scenarios = scenarios
        self.options = options

    def run(self):
        """Start Felt run and execute watchdog."""
        if self.options.isVerbose():
            print("################################")
            print("\tFelt (%s)" % __version__)
            print("################################")

        if self.options.getMaximumExectionTime() > 0:
            self.initWatchdog()

        worker = WebworkerService()
        return worker.run(self.options, self.scenarios)

    def initWatchdog(self):
        """Init watchdog and kill thread after x seconds."""
        def watchdog(sec):
            """ Stops the process after x seconds."""
            time.sleep(sec)
            sys.exit(0)

        Thread(
            target=watchdog,
            args=(self.options.getMaximumExectionTime(),)
        ).start()


# Initiate thread and dataqueue
threadQueue = Queue()
dataQueue = Queue()


class WebworkerService:
    """WebworkerService class."""

    def run(self, options, scenarios):
        """Run function.

        Init run of main workload loop
        """
        self.threadcount = 0
        self.threadstarted = 0
        self.running = True
        self.scenario = 0

        # Start new one every minute
        while self.running:
            self.startRun(scenarios, options)

            # Keep track of running threads
            try:
                while True:
                    threadQueue.get(False)
                    self.threadcount -= 1

                    # Test mode
                    if options.isTest():
                        self.running = False

            except Empty:
                pass

            time.sleep(0.25)

        # Parse data coming from threads
        data = []
        try:
            while True:
                rawData = dataQueue.get(False)
                if rawData.strip() == '':
                    continue

                parsedRows = json.loads(rawData)
                if parsedRows['type'] == 'results':
                    for row in parsedRows['data']:
                        # We need to decode the step string
                        row['step'] = json.loads(row['step'])
                    data.append(parsedRows)
        except Empty:
            pass
        except ValueError:
            if options.isDebug():
                raise ValueError(
                    "Unable to parse data coming from worker: '%s'" % rawData
                )
            else:
                raise ValueError("Unable to parse data coming from worker")

        if options.isDebug():
            print(json.dumps(data, indent=4, sort_keys=True))

        return data

    def startRun(self, scenarios, options):
        """Initiate run."""
        if (options.getThreads() > self.threadcount):
            # Start threads
            for x in range(options.getThreads() - self.threadcount):
                self.threadcount += 1
                self.threadstarted += 1
                Thread(
                    target=WebworkerService.execute,
                    args=(
                        self.threadstarted,
                        scenarios[self.scenario],
                        options,
                    )
                ).start()

                # Go to next scenario
                self.scenario += 1
                if self.scenario > len(scenarios) - 1:
                    self.scenario = 0

    @staticmethod
    def execute(threadId, scenario, options):
        """Execute browser thread with options."""

        # Prepare command statement
        pathJs = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'js/worker.js'
        )

        command = [
            options.getBrowserPath(),
            pathJs,
            str(threadId),
            json.dumps(scenario.preprocessScenario()),
            json.dumps(options.getRunnerOptions())
        ]

        # Execute and send output to PIPE
        process = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        # Set correct encoding or default to UTF-8
        encoding = sys.stdout.encoding
        if encoding is None:
            encoding = 'UTF-8'

        # Main output loop
        while True:
            nextline = process.stdout.readline().decode(encoding)
            dataQueue.put(nextline)

            if process.poll() is not None:
                threadQueue.put("Something")
                break

        # TODO: Handle this returncode
        print("Returncode: %s" % process.returncode)

        return None
