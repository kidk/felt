import unittest

loader = unittest.TestLoader()
tests = loader.discover('tests', pattern='*.py')
testRunner = unittest.runner.TextTestRunner()
testRunner.run(tests)
