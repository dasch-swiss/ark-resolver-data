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

## Example project configuration

An example project configuration in the `data/dasch_ark_registry.ini` file looks like this:

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
Host: admin.dasch.swiss

# The hostname to be used in redirect URL for this project's metadata.
ProjectHost: project-metadata.dasch.swiss

# The template to be used for generating redirect URLs referring to DSP values.
DSPValueRedirectUrl : https://values.dasch.swiss/value/$resource_iri/$value_id

# true if the PHP-based server should be used for this project (i.e. if project is on Salsah)
UsePhp: true

# true if this project can accept version 0 ARK URLs
AllowVersion0: true
```

## Example of ARK redirects

The following ARK of a resource:
```bash
http://ark.dasch.swiss/ark:/72163/1/ABCD/t8I=deu9SuajedJ2vys6iAY.20210915T170737243528Z
```
interpreted as:
```bash
http://ark.dasch.swiss/ark:/72163/1/[$project_id]/[$resource_id]
```
is redirected to:
```bash
https://admin.dasch.swiss/resource/http:%2F%2Frdfh.ch%2FABCD%2Ft8I-deu9SuajedJ2vys6iA?version=20210915T170737243528Z
```
interpreted as:
```bash
https://admin.dasch.swiss/resource/http:%2F%2Frdfh.ch%[$project_id]%2F[$resource_id]
```

## Example of the configuration of a custom project ARK redirect pattern

The following example shows how to change the default behavior of project ARK redirects.

An ARK of a project looks like this: `http://ark.dasch.swiss/ark:/72163/1/ABCD` for project with short code `ABCD`. Per
default, it is redirected to `https://meta.dasch.swiss/projects/ABCD`.

If this behaviour should be changed for a project, either set another host for your project ARK (variable `ProjectHost` 
in the file data/dasch_ark_registry.ini). For example:

```
[ABCD]
Host: admin.dasch.swiss
ProjectHost: meta.dasch.swiss
```

This would redirect the ARK `http://ark.dasch.swiss/ark:/72163/1/ABCD` to `https://meta.dasch.swiss/projects/ABCD`.
So, only the host is changed. Or you can set the variable `DSPProjectRedirectUrl` with your own pattern or a hard coded
URL. For example:

```
[ABCD]
Host: admin.dasch.swiss
DSPProjectRedirectUrl: http://other/host/my/pattern/$project_ids
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
