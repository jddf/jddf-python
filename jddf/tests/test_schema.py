import json
import unittest
from jddf import Schema


class TestSchema(unittest.TestCase):
    def test_invalid_schemas(self):
        with open("spec/tests/invalid-schemas.json") as f:
            test_cases = json.loads(f.read())
            for test_case in test_cases:
                with self.subTest(test_case['name']):
                    ok = False
                    try:
                        Schema.from_json(test_case['schema']).verify()
                    except TypeError:
                        ok = True

                    self.assertTrue(ok)
