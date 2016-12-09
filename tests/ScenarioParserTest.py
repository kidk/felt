import unittest
from models import Scenario


class ScenarioParserTest(unittest.TestCase):

    def test_single(self):
        scenario = Scenario({
            "variables": [
                {
                    "type": "constant",
                    "value": "constant_string",
                    "name": "some_var"
                }
            ],
            "steps": [
                {
                    "action": "set_value",
                    "selector": "element",
                    "value": "$[some_var]"
                }
            ]
        })

        self.assertEqual(scenario.preprocessScenario(), [
            {
                'action': 'set_value',
                'value': 'constant_string',
                'selector': 'element'
            }
        ])

    def test_multiple(self):
        scenario = Scenario({
            "variables": [
                {
                    "type": "constant",
                    "value": "1",
                    "name": "first_var"
                },
                {
                    "type": "constant",
                    "value": "$[first_var]2",
                    "name": "second_var"
                },
                {
                    "type": "constant",
                    "value": "$[second_var]3",
                    "name": "third_var"
                }
            ],
            "steps": [
                {
                    "action": "set_value",
                    "selector": "element",
                    "value": "$[third_var]"
                }
            ]
        })

        self.assertEqual(scenario.preprocessScenario(), [
            {
                'action': 'set_value',
                'value': '123',
                'selector': 'element'
            }
        ])

    def test_random(self):
        scenario = Scenario({
            "variables": [
                {
                    "type": "randomString",
                    "length": 10,
                    "name": "random"
                }
            ],
            "steps": [
                {
                    "action": "set_value",
                    "selector": "input#random",
                    "value": "$[random]"
                }
            ]
        })

        # Take first element
        element = scenario.preprocessScenario()[0]
        self.assertNotEqual(element['value'], "")
        self.assertEqual(element["action"], "set_value")
        self.assertEqual(element["selector"], "input#random")


if __name__ == '__main__':
    unittest.main()
