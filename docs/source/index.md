# jddf

Welcome to the online documentation for `jddf`. `jddf` is a Python
implementation of [JSON Data Definition Format][jddf], a schema language for
JSON.

[jddf]: https://jddf.io

For specific documentation of the classes and constants this package exposes,
see the [API docs for the `jddf` module](jddf).

For more details on this project, consult the project README here:

> [https://github.com/jddf/jddf-python](https://github.com/jddf/jddf-python)

Briefly, here's how you would use this package:

```python3
import Schema, Validator from jddf
import json

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

validator = Validator()

errors_ok = validator.validate(schema, json.loads("""
  {
    "name": "John Doe",
    "age": 43,
    "phones": ["+44 1234567", "+44 2345678"]
  }
"""))

print(errors_ok) # []

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
