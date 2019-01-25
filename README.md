# DaSCH Ark Resolver Data

This repository holds data for the DaSCH Ark Resolver service running
at https://ark.dasch.swiss.

## How to add a new project?

Create a new branch and do the following:

1. Add the new project to the `data/shortcodes.csv` file and
   assigning it a free project shortcode.

2. Add the new shortcode to the `data/dasch_ark_registry.ini` file.
   See existing entries for guidance or see https://github.com/dhlab-basel/ark-resolver.

3. Add a new test to the `tests/` directory with the name `test_shortcode.tavern.yaml`.
   See existing tests for guidance.

4. Create a new PR.

## Requirements

To install the requirements:

```bash
$ pip3 install -r requirements.txt
```


To generate a "requirements" file (usually requirements.txt), that you commit with your project, do:

```bash
$ pip3 freeze > requirements.txt
```
