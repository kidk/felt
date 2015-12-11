import argparse
import subprocess
import sys
from Queue import Queue, Empty

import time
from threading import Thread

__author__ = 'CoScale - Samuel Vandamme (samuel@sava.be) '

threadQueue = Queue()


def main(args):
    """ The main function parses the command line arguments, reads the input file and starts the
    generator. """

    # Parse arguments
    parser = argparse.ArgumentParser(description='Start workload.')
    parser.add_argument('-url', '--url', type=str, required=True,
                        help="url to open until halted")
    args = parser.parse_args()

    worker = WebworkerService()
    worker.run(args.url)


class WebworkerService:


    def run(self, url):
        self.threadcount = 0

        # Start new one every minute
        while True:
            self.startRun(url)

            # Keep track of running threads
            try:
                while True:
                    threadQueue.get(False)

                    self.threadcount -= 1

                    threadQueue.task_done()
            except Empty, e:
                pass

            time.sleep(0.25)

    def startRun(self, url):
        if (5 > self.threadcount):
            # Start threads
            for x in range(5 - self.threadcount):
                self.threadcount += 1
                Thread(target=execute, args = (url, )).start()



def execute(url):
    command = ['./phantomjs', 'js/worker.js', "--url=" + url];
    print command
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        nextline = process.stdout.readline()
        sys.stdout.write(nextline)
        sys.stdout.flush()

        if process.poll() != None:
            threadQueue.put("Something")
            break


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
