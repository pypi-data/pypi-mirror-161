# Python code wake SQL Academy 1.4 store adapter (pycodewake-sql13-store)

[![test](https://github.com/mwri/pycodewake-sql13-store/actions/workflows/test.yml/badge.svg)](https://github.com/mwri/pycodewake-sql13-store/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/mwri/pycodewake-sql13-store/branch/main/graph/badge.svg)](https://codecov.io/gh/mwri/pycodewake-sql13-store)

This store adapter provides backing via SQL Academy 1.3 for Code Wake.
Use pycodewake-sql14-store if you are integrating with SQL Alchemy 1.4.

For example:

```python
import code_wake
from code_wake_sql13_store import Sql13Store

cwproc = code_wake.Process(
    app_name="my_app",
    app_vsn="1.2.3",
    env_name="production",
    store=Sql13Store("sqlite:////tmp/some_file.sqlite"),
)
```
