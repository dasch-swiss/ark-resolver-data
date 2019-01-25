# DaSCH Ark Resolver Data

This repository holds data for the DaSCH Ark Resolver service running
at https://ark.dasch.swiss.

## Add new project

1. Add the new project to the `data/shortcodes.md` file and
   assigning it a free project shortcode.

2. Add the new shortcode to the `data/dasch_ark_registry.ini` file, following
   existing entries.

3. Add a new test to the `tests/` directory with the name `shortcode_test.tavern.yaml`.

## Requirements

To install the requirements:

```bash
$ pip3 install -r requirements.txt
```


To generate a "requirements" file (usually requirements.txt), that you commit with your project, do:

```bash
$ pip3 freeze > requirements.txt
```
