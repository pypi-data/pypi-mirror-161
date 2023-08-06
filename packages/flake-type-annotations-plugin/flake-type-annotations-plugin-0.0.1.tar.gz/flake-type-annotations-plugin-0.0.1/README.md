## Flake type annotations plugin

The `flake8` plugin checking for correct usage of the Python type annotations.

## Installation

Plugin requires `flake8 >3.0.0`

```bash
pip install flake-type-annotations-plugin
```

## Rules

### `ANN001`

This rule disallows usage of `Union` and `Optional` type annotations and expects user 
to use the new `|` operator syntax.

Example:

```python
# WRONG
from typing import Optional, Union

def func(arg: Optional[int]) -> Union[int, str]:  # violates ANN001
    return arg if arg is not None else "N/A"

# CORRECT
def func(arg: int | None) -> int | str:  # OK
    return arg if arg is not None else "N/A"
```

For Python versions `<3.10` a top-level module import 
`from __future__ import annotations` must be included in order to use this 
syntax.

More can be read in [PEP604](https://peps.python.org/pep-0604/).

### `ANN002`

This rule disallows usage of type annotations where built-in types can be used.

Example:

```python
# WRONG
from typing import List, Tuple

def func(arg: Tuple[int]) -> List[int]:  # violates ANN002
    return list(arg)

# CORRECT
def func(arg: tuple[int]) -> list[int]:  # OK
    return list(arg)
```

For Python versions `<3.9` a top-level module import
`from __future__ import annotations` must be included in order to use this
syntax.

More can be read in [PEP585](https://peps.python.org/pep-0585/).
