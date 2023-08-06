## terrorform

Python wrapper for [Terraform](https://www.terraform.io/)

### Purpose

This library provides a thin wrapper around the Terraform build tool. Existing libraries for the same purpose were
either more complicated than what I needed or defunct. The name `terrorform` was chosen because every other name I 
could think of was being squatted on in PyPi. 

### Package Installation and Usage

The package is available on [PyPi](https://pypi.org/project/terrorform/0.1.0/):
```shell
python -m pip install terrorform
```

The library can be imported in the normal ways:
```python
import terrorform
from terrorform import *
```

### Examples

This library supports `init`, `apply`, and `destroy` workflows:

```python
from terrorform import *

# Run full setup/teardown workflow with target directory equal to current working directory
init_resp = terrorform.init()
apply_resp = terrorform.apply()
destroy_resp = terrorform.destroy()
```

The library also supports top level synonyms, allowing the same workflows to be run without 
referencing the `terrorform` class:

```python
from terrorform import *

init_resp = init()
apply_resp = apply()
destroy_resp = destroy()
```

Keyword arguments, boolean flags, and custom variables are passed to each workflow. No checking
is performed to ensure that they are valid terraform CLI options. These parameters are split into
three categories: keyword arguments, boolean flags, and custom variables:

```python
apply_resp = terrorform.apply(
    # Terraform-specific keyword args, both global and non-global
    kw_args={
        "-chdir": "/tmp/terrorform/"
    },
    # Terraform-specific boolean flags
    boolean_flags=["-no-color"],
    # Custom variables required by your terraform scripts
    vars_dict={
        "my_custom_variable": "Hello"
    }
)
```


### Testing

Tests are run using `pytest`:

```shell
python -m pytest tests.py
```