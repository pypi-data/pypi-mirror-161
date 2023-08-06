# hangarmc-hangar

pythonic type-hinted [hangar](https://github.com/HangarMC/Hangar) API wrapper

## Installation

hangarmc-hangar requires python 3.9 or above

```shell
# PIP3
pip3 install hangarmc-hangar
# PIP
pip install hangarmc-hangar
# Poetry
poetry add hangarmc-hangar
```

## API

All functions and classes are properly type hinted and documented with quotes/comments. Please file an issue or pull
request if any issues are found.

### Basic Usage

#### Example

```python
from hangarmc_hangar import Hangar, HangarApiException

# Create an SDK instance
hangar = Hangar()

try:
    # Get all projects
    projects = hangar.search_projects()
    # Output data
    print(f"Project amount: {projects.pagination.count}")
    for project in projects.result:
        print(project.name)
except HangarApiException as e:
    raise

```

#### Output

```shell
$ python sketch.py
Project amount: 32
CoolProject
NotQuests
EndBiomeFixer
... and on
```
