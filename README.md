# jddf-python [![PyPI version](https://badge.fury.io/py/jddf.svg)](https://badge.fury.io/py/jddf)

> Documentation on readthedocs.io: https://jddf.readthedocs.io

This package is a Python implementation of [JSON Data Definition Format][jddf],
a schema language for JSON.

[jddf]: https://jddf.io

## Installation

Install this package using:

```bash
pip3 install jddf
```

## Usage

Briefly, here's how you would use this package:

```python
import Schema, Validator from jddf
import json

# jddf.Schema represents a JDDF Schema.
#
# You can parse a jddf.Schema from JSON using Schema.from_json in combination
# with the standard library's json module.
schema = Schema.from_json(json.loads("""
  {
    "properties": {
      "name": { "type": "string" },
      "age": { "type": "uint32" },
      "phones": {
        "elements": { "type": "string" }
      }
    }
  }
"""))

# jddf.Validator validates inputted data against schemas, and returns a list of
# validation errors.
#
# The exact data in validation errors is part of the JDDF specification, so
# every implementation of JDDF, across all languages, return the same sort of
# validation errors.
validator = Validator()

# This input is ok -- it passes all of the rules of the schema. So no validation
# errors are returned.
errors_ok = validator.validate(schema, json.loads("""
  {
    "name": "John Doe",
    "age": 43,
    "phones": ["+44 1234567", "+44 2345678"]
  }
"""))

print(errors_ok) # []

# This input has three problems, so three validation errors are returned.
errors_bad = validator.validate(schema, json.loads("""
  {
    "age": "43",
    "phones": ["+44 1234567", 442345678]
  }
"""))

print(len(errors_bad)) # 3

# "name" is required
#
# [{'instance_path': [], 'schema_path': ['properties', 'name']}]
print(errors_bad[0])

# "age" has wrong type
#
# [{'instance_path': ['age'], 'schema_path': ['properties', 'age', 'type']}]
print(errors_bad[1])

# "phones[1]" has wrong type
#
# [{'instance_path': ['phones', '1'], 'schema_path': ['properties', 'phones', 'elements', 'type']}]
print(errors_bad[2])
```
