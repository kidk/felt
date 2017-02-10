import unittest

from core import Felt
from models import Scenario, Options


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

        self.assertEqual(2, len(result))

        # Check action 1
        self.assertLess(result[0]['start'], result[0]['end'])
        self.assertTrue(result[0]['success'])
        self.assertEquals(
            result[0]['time'],
            result[0]['end'] - result[0]['start']
        )
        self.assertEquals('https://felt.sava.be/', result[0]['url'])
        self.assertEquals('open_url', result[0]['step']['action'])
        self.assertEquals('https://felt.sava.be/', result[0]['step']['value'])

        # Check action 2
        self.assertLess(result[1]['start'], result[1]['end'])
        self.assertTrue(result[1]['success'])
        self.assertEquals(
            result[1]['time'],
            result[1]['end'] - result[1]['start']
        )
        self.assertEquals(
            'https://felt.sava.be/settings.php', 
            result[1]['url']
        )
        self.assertEquals('click', result[1]['step']['action'])
        self.assertEquals(
            '#navbar > ul > li:nth-child(2) > a',
            result[1]['step']['selector']
        )

    def runTest(self, scenario):
        options = Options()
        options.setTest(True)

        core = Felt(options, scenario)
        result = core.run()

        self.assertEqual(1, len(result))

        return result[0]
