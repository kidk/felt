"""Test file for Felt."""

import unittest
import sys

print "Starting test run"

loader = unittest.TestLoader()
tests = loader.discover('tests', pattern='*.py')
testRunner = unittest.runner.TextTestRunner()
result = testRunner.run(tests)

sys.exit(len(result.errors) + len(result.failures))
