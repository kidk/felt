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

    def __init__(self, options, scenario):
        """Init vars."""
        self.scenario = scenario
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
        return worker.run(self.scenario, self.options)

    def initWatchdog(self):
        """Init watchdog and kill thread after x seconds."""
        def watchdog(sec):
            """ Stops the process after x seconds."""
            time.sleep(sec)
            os._exit(0)

        Thread(
            target=watchdog,
            args=(self.options.getMaximumExectionTime(),)
        ).start()


# Initiate thread and dataqueue
threadQueue = Queue()
dataQueue = Queue()


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

                    # Test mode
                    if options.isTest():
                        self.running = False

            except Empty:
                pass

            time.sleep(0.25)

        # Parse data coming from threads
        data = []
        parsedRows = ""
        try:
            while True:
                rawData = dataQueue.get(False)

                parsedRows = json.loads(rawData)
                for row in parsedRows:
                    # We need to decode the step string
                    row['step'] = json.loads(row['step'])
                data.append(parsedRows)
        except Empty:
            pass
        except ValueError:
            if options.isDebug():
                raise ValueError(
                    "Unable to parse data coming from worker: " + rawData
                )
            else:
                raise ValueError("Unable to parse data coming from worker")

        return data

    def startRun(self, scenario, options):
        """Initiate run."""
        if (options.getThreads() > self.threadcount):
            # Start threads
            for x in range(options.getThreads() - self.threadcount):
                self.threadcount += 1
                self.threadstarted += 1
                Thread(
                    target=WebworkerService.execute,
                    args=(self.threadstarted, scenario, options, )
                ).start()

    @staticmethod
    def execute(threadId, scenario, options):
        """Execute browser thread with options."""
        command = [
            options.getBrowser(),
            'worker.js',
            str(threadId),
            json.dumps(scenario.preprocessScenario()),
            json.dumps(options.getRunnerOptions())
        ]
        print(command)
        process = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        # Main loop
        data = ""

        while True:
            nextline = process.stdout.readline()
            data += nextline.decode(sys.stdout.encoding)

            if process.poll() is not None:
                dataQueue.put(data)
                threadQueue.put("Something")
                break

        return None
