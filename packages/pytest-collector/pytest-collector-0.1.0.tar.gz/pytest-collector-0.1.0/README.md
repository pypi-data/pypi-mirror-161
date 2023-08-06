# pytest-collector
Python package for collecting pytest tests.

## Usage

`pip install pytest-collector`

```
import pytest_collector

# NOTE: this call will import the tests to the current process.
test_modules = pytest_collector.collect("path/to/tests/directory")
```