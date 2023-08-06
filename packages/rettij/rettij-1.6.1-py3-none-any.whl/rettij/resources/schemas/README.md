# Topology JSON-schemas

The file `topology_schema.json` describes the formal conventions which a topology must follow using the JSON-schema specification (http://json-schema.org/).

## Versioning
Each version of the topology file format has a corresponding schema.
These are placed in the `x.x` directories.
rettij will automatically select the schema matching its supported topology version.

## File structure

The file `topology_schema.json` acts as the main schema which contains references to `channel_schema.json` and `node_schema.json`, where the latter includes `interface_schema.json` to describe an interface of a node.

## Validations

JSON-schema uses different keys to implement different types of validations.

#### Pattern validation
Using the `pattern` key, an attribute can be validated using a regular expression, e.g. in `interface_schema.json`, testing the formal correctness of a Mac address:
```json
"mac": {
  "type": "string",
  "description": "",
  "pattern": "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
  "error_msg": "mac address not valid"
}
```

#### Conditional requirements
Using the keys `if` and `then` a JSON-schema can conditionally require attributes, for example if a node of type switch requires the interface-attribute to be set:
```json
"if": {
  "properties": {
    "type": {
      "oneOf": [
        {
          "const": "switch"
        },
      ]
    }
  }
},
"then": {
  "required": [
    "interfaces"
  ]
}
```

If multiple `if`/`then` validations are needed, they have to be wrapped in an `allOf` key, since JSON otherwise overwrites the `if` key due to not allowing duplicate keys.