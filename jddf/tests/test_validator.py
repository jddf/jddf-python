import unittest
import glob
import json
import jddf
from typing import List


class TestValidator(unittest.TestCase):
    def test_max_depth(self):
        schema = jddf.Schema(definitions={"x": jddf.Schema(ref="x")}, ref="x")
        validator = jddf.Validator(max_depth=5)
        with self.assertRaises(jddf.MaxDepthExceededError):
            validator.validate(schema, None)

    def test_max_errors(self):
        schema = jddf.Schema(elements=jddf.Schema(type="string"))
        validator = jddf.Validator(max_errors=3)
        errors = validator.validate(schema, [None, None, None, None, None])
        self.assertEqual(len(errors), 3)

    def test_spec(self):
        for path in glob.glob('spec/tests/validation/*'):
            with open(path) as f:
                test_suites = json.loads(f.read())
                for test_suite in test_suites:
                    for index, test_case in enumerate(test_suite['instances']):
                        with self.subTest(test_suite['name'], index=index):
                            expected = [jddf.ValidationError(self._parse_json_pointer(
                                e['instancePath']), self._parse_json_pointer(e['schemaPath'])) for e in test_case['errors']]

                            validator = jddf.Validator()
                            schema = jddf.Schema.from_json(
                                test_suite['schema']).verify()
                            actual = validator.validate(
                                schema, test_case['instance'])

                            self.assertEqual(sorted(actual, key=lambda e: e.instance_path), sorted(
                                expected, key=lambda e: e.instance_path))

    def _parse_json_pointer(self, ptr: str) -> List[str]:
        return ptr.split('/')[1:]
