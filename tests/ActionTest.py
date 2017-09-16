import unittest

from felt.core import Felt
from felt.models import Scenario, Options
from felt.init import init


class ScenarioParserTest(unittest.TestCase):

    def test_click(self):
        scenario = Scenario({
            "variables": [],
            "steps": [
                {
                    "action": "load",
                    "url": "http://localhost:5555/simple/"
                },
                {
                    "action": "event",
                    "type": "click",
                    "element": "#navbar > ul > li:nth-child(2) > a",
                }
            ]
        })
        result = self.runTest(scenario)

        # Check for results
        self.assertEqual("results", result['type'])
        self.assertEqual(3, len(result['data']))

        # Retrieve data
        data = result['data']
        action1 = data[0]
        # action2 = data[1]
        action3 = data[2]

        # Check action 1
        self.assertLess(action1['start'], action1['end'])
        self.assertTrue(action1['success'])
        self.assertEquals(
            action1['time'],
            action1['end'] - action1['start']
        )
        self.assertEquals('http://localhost:5555/simple/', action1['url'])
        self.assertEquals('load', action1['step']['action'])
        self.assertEquals(
            'http://localhost:5555/simple/',
            action1['step']['url']
        )

        # Check action 3
        self.assertLess(action3['start'], action3['end'])
        self.assertTrue(action3['success'])
        self.assertEquals(
            action3['time'],
            action3['end'] - action3['start']
        )
        self.assertEquals(
            'http://localhost:5555/simple/settings.php',
            action3['url']
        )
        self.assertEquals('event', action3['step']['action'])
        self.assertEquals('click', action3['step']['type'])
        self.assertEquals(
            '#navbar > ul > li:nth-child(2) > a',
            action3['step']['element']
        )

    def test_login(self):
        scenario = Scenario({
            "variables": [],
            "steps": [
                {
                    "action": "load",
                    "url": "http://localhost:5555/simple/"
                },
                {
                    "action": "set",
                    "attribute": "value",
                    "selector": "input[name=username]",
                    "value": "felt"
                },
                {
                    "action": "set",
                    "attribute": "value",
                    "selector": "input[name=password]",
                    "value": "isAWESOME"
                },
                {
                    "action": "wait",
                    "time": {
                        "min": 1000,
                        "max": 5000
                    }
                },
                {
                    "action": "event",
                    "type": "submit",
                    "selector": "#loginForm"
                }
            ]
        })
        result = self.runTest(scenario)

        print result

        # Check for results
        self.assertEqual("results", result['type'])
        self.assertEqual(5, len(result['data']))

        # Retrieve data
        # data = result['data']
        # action1 = data[0]
        # action2 = data[1]
        # action3 = data[2]
        # action4 = data[3]
        # action5 = data[4]

    def runTest(self, scenario):
        options = Options()
        options.setTest(True)
        options.setDebug(True)
        init(options)

        core = Felt(options, [scenario])
        result = core.run()

        self.assertEqual(1, len(result))

        return result[0]
