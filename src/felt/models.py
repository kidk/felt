import random
import copy
import json
import string


__license__ = "MIT"
__maintainer__ = "Samuel Vandamme"
__email__ = "samuel@sava.be"
__author__ = "Samuel Vandamme"
__credits__ = ["Stijn Polfliet", "Samuel Vandamme", "Hatem Mostafa"]
__version__ = "alpha"


class Options:

    DEFAULT_THREADS = 5
    DEFAULT_VERBOSE = False
    DEFAULT_DEBUG = False
    DEFAULT_MAXTIME = 0
    DEFAULT_TEST = False
    DEFAULT_BROWSER = 'phantomjs'
    DEFAULT_SCREENSHOT = False
    DEFAULT_USERAGENT = 'Mozilla/5.0 (X11; Linux i686; rv:10.0)' + \
        ' Gecko/20100101 Firefox/10.0'

    def __init__(self):
        self._threads = Options.DEFAULT_THREADS
        self._verbose = Options.DEFAULT_VERBOSE
        self._debug = Options.DEFAULT_DEBUG
        self._maxTime = Options.DEFAULT_MAXTIME
        self._test = Options.DEFAULT_TEST
        self._browser = Options.DEFAULT_BROWSER
        self._screenshot = Options.DEFAULT_SCREENSHOT
        self._userAgent = Options.DEFAULT_USERAGENT
        self._browserPath = {
            'phantomjs': "",
            'slimerjs': ""
        }

    def setThreads(self, threads):
        if (self._test):
            print("Error: Only 1 thread allowed in test mode")
            return

        self._threads = threads

    def setVerbose(self, verbose):
        self._verbose = verbose

    def setDebug(self, debug):
        self._debug = debug

    def setMaximumExectionTime(self, maximum):
        self._maxTime = maximum

    def setBrowser(self, browser):
        self._browser = browser

    def setScreenshot(self, screenshot):
        self._screenshot = screenshot

    def setUserAgent(self, userAgent):
        self._userAgent = userAgent

    def setTest(self, test):
        self._test = test
        self._threads = 1

    def setBrowserPath(self, browser, path):
        self._browserPath[browser] = path

    def getThreads(self):
        return self._threads

    def getMaximumExectionTime(self):
        return self._maxTime

    def getBrowser(self):
        return self._browser

    def getUserAgent(self):
        return self._userAgent

    def getScreenshot(self):
        return self._screenshot

    def isVerbose(self):
        return self._verbose

    def isTest(self):
        return self._test

    def isDebug(self):
        return self._debug

    def getRunnerOptions(self):
        return {
            'debug': self.isDebug(),
            'verbose': self.isVerbose(),
            'screenshot': self.getScreenshot(),
            'userAgent': self.getUserAgent()
        }

    def getBrowserPath(self):
        return self._browserPath[self.getBrowser()]


class Scenario():
    def __init__(self, scenario):
        self._scenario = scenario

    def preprocessScenario(self):
        """Preprocess the scenario so that the variables are filled in."""
        obj = copy.deepcopy(self._scenario)
        variables = []
        if 'variables' in obj:
            variables = copy.deepcopy(obj['variables'])
        steps = copy.deepcopy(obj['steps'])

        # Loop all variables
        for idx in range(len(variables)):

            # Current variable
            variable = variables[idx]

            # Type
            varType = variable['type']

            searchForExactMatch = False

            # Fetch value of variable
            if varType == 'randomString':
                value = self.getRandomString(variable['length'])
            elif varType == 'constant':
                value = variable['value']
                if isinstance(value, list):
                    # We will be searching for exact match in case of arrays
                    # because we will replace the whole variable.
                    searchForExactMatch = True
            # Error message in case unknown type
            else:
                value = None
                print('Unknown variable type `%s`' % variable['type'])

            # If valid variable
            if value is not None:
                # Replacing the variable name with
                # its value in the following variables.

                # String to find
                vsyntax = '$[' + variable['name'] + ']'

                # Loop variables after current one
                for idx2 in range(idx + 1, len(variables)):
                    variable2 = variables[idx2]
                    if 'value' in variable2:
                        if searchForExactMatch:
                            if variable2['value'] == vsyntax:
                                variable2['value'] = value
                        else:
                            variable2['value'] = json.loads(
                                json.dumps(variable2['value'])
                                    .replace(vsyntax, value))

                # Replacing the variable name with its value in the steps.
                for step in steps:
                    if 'value' in step:
                        if searchForExactMatch:
                            if step['value'] == vsyntax:
                                step['value'] = value
                        else:
                            step['value'] = json.loads(
                                json.dumps(step['value'])
                                    .replace(vsyntax, value))

        return steps

    def getRandomString(
        self,
        size=6,
        chars=string.ascii_lowercase + string.digits
    ):
        """Generate random string."""
        return ''.join(random.choice(chars) for x in range(size))
