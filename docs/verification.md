# Problem format validation

This repository owns the [problem contract](contract.md) and checks its machine-readable values and manifests before publication. Run this command from the repository root with Python 3.11 or newer:

```sh
python3 tools/validate.py
```

The validator reads `contract.toml`, discovers `challenges/*/challenge.toml`, and checks the contract version, required fields, types, allowed values, file and service rules, endpoint declarations, and patch declarations. Declared distribution and Compose paths must exist inside this repository, including their symlink targets. Errors identify the manifest and offending field.

Run the format validator's regression checks with:

```sh
python3 -B -m unittest discover -s tools -p 'test_*.py'
```

Both commands use Python's standard library and run with this repository alone.
