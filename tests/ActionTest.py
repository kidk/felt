import unittest
import json

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
                    "url": "https://felt.sava.be/"
                },
                {
                    "action": "event",
                    "type": "click",
                    "element": "#navbar > ul > li:nth-child(2) > a",
                }
            ]
        })

        result = self.runTest(scenario)

        print json.dumps(result, indent=4, sort_keys=True)

        self.assertEqual("results", result['type'])
        self.assertEqual(2, len(result['data']))

        data = result['data']

        # Check action 1
        self.assertLess(data[0]['start'], data[0]['end'])
        self.assertTrue(data[0]['success'])
        self.assertEquals(
            data[0]['time'],
            data[0]['end'] - data[0]['start']
        )
        self.assertEquals('https://felt.sava.be/', data[0]['url'])
        self.assertEquals('load', data[0]['step']['action'])
        self.assertEquals('https://felt.sava.be/', data[0]['step']['url'])

        # Check action 2
        self.assertLess(data[1]['start'], data[1]['end'])
        self.assertTrue(data[1]['success'])
        self.assertEquals(
            data[1]['time'],
            data[1]['end'] - data[1]['start']
        )
        self.assertEquals(
            'https://felt.sava.be/settings.php',
            data[1]['url']
        )
        self.assertEquals('event', data[1]['step']['action'])
        self.assertEquals('click', data[1]['step']['type'])
        self.assertEquals(
            '#navbar > ul > li:nth-child(2) > a',
            data[1]['step']['element']
        )

    def runTest(self, scenario):
        options = Options()
        options.setTest(True)
        init(options)

        core = Felt(options, [scenario])
        result = core.run()

        self.assertEqual(1, len(result))

        return result[0]
