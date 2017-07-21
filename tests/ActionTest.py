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
                    "action": "open_url",
                    "value": "https://felt.sava.be/"
                },
                {
                    "action": "click",
                    "selector": "#navbar > ul > li:nth-child(2) > a",
                }
            ]
        })

        result = self.runTest(scenario)

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
        self.assertEquals('open_url', data[0]['step']['action'])
        self.assertEquals('https://felt.sava.be/', data[0]['step']['value'])

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
        self.assertEquals('click', data[1]['step']['action'])
        self.assertEquals(
            '#navbar > ul > li:nth-child(2) > a',
            data[1]['step']['selector']
        )

    def runTest(self, scenario):
        options = Options()
        options.setTest(True)
        init(options)

        core = Felt(options, [scenario])
        result = core.run()

        self.assertEqual(1, len(result))

        return result[0]
