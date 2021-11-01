# DaSCH Ark Resolver Data

This repository holds data for the DaSCH Ark Resolver service running at https://ark.dasch.swiss.

## How to add a new project?

Create a branch and do the following:

1. Add the project to the `data/shortcodes.csv` file with its shortcode, shortname, long name and old Salsah ID.

2. Add the project's shortcode to the `data/dasch_ark_registry.ini` file (`data/dasch_ark_registry_test.ini` or
   `data/dasch_ark_registry_staging.ini` if you want to add a configuration to test or staging). See example below or
   existing entries for guidance or see https://github.com/dasch-swiss/ark-resolver.

3. Add a new test to the `tests/` directory with the name `test_shortcode.tavern.yaml`. See existing tests for guidance.

4. Create a new PR.

## Example project

```bash 
############################################################################
# Example Project

# The project's shortcode (`[...]`) and resources host (`Host`) are mandatory. All other parameters can be left out if 
# not used. A default value / template is used in this case. Default templates are defined in the top section of 
# dasch_ark_registry.ini. By setting the parameter in the project's section of the file, the default value / template is
# overwritten.

# The project's shortcode
[ABCD]

# The hostname to be used in redirect URLs for this project's resources.
Host: data.dasch.swiss

# The hostname to be used in redirect URL for this project's metadata.
ProjectHost: project-metadata.dasch.swiss

# The template to be used for generating redirect URLs referring to DSP values.
DSPValueRedirectUrl : https://values.dasch.swiss/value/$resource_iri/$value_id

# true if the PHP-based server should be used for this project (i.e. if project is on Salsah)
UsePhp: true

# true if this project can accept version 0 ARK URLs
AllowVersion0: true
```

## Requirements

To install the requirements:

```bash
$ pip3 install -r requirements.txt
```

To generate the requirements file (requirements.txt), that you commit with the project, do:

```bash
$ pip3 freeze > requirements.txt
```
