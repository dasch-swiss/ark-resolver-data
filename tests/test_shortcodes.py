"""
Checks every shortcode registered in ../data/dasch_ark_registry.ini, instead
of requiring one hand-written test file per shortcode.

Two things are checked, each against a different kind of mistake:

- The redirect tests predict the redirect URL by substituting the project's
  own INI templates the same way ark-resolver does (see
  https://github.com/dasch-swiss/ark-resolver, `src/ark_url.py` at tag
  v1.7.4, the image pinned in docker-compose.yml), then assert the local
  resolver's actual response (started via `make test`) matches. Since the
  prediction and the resolver read the same INI, this cannot catch a
  plausible-but-wrong value (a Host typo, for example) -- only a template
  that's malformed for the fields it's given (an undefined `$variable`,
  say) or a resolver that no longer behaves the way its own code documents.

- test_shortcode_listed_in_shortcodes_md is a genuinely independent check:
  every shortcode added to the INI must also be registered in
  ../data/shortcodes.md, per the order of steps in ../README.md. It runs
  without the resolver.
"""

import configparser
import re
from pathlib import Path
from string import Template
from urllib.parse import quote

import pytest
import requests

RESOLVER_URL = "http://127.0.0.1:3336"
NAAN = "72163"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REGISTRY_PATH = DATA_DIR / "dasch_ark_registry.ini"
SHORTCODES_MD_PATH = DATA_DIR / "shortcodes.md"

# Any base64url string works as a resource ID: the check digit is computed
# from the ID's own characters only, independent of the project shortcode.
DSP_RAW_RESOURCE_ID = "-6IqRiuwQHGbHWuy2O8Bfg"
# The PHP redirect path parses the resource ID as hex (`int(id, 16)`), so it
# needs its own, hex-only raw ID.
PHP_RAW_RESOURCE_ID = "1A2B3C4D5E6F"
TIMESTAMP = "20191217T111513000Z"
RESOURCE_INT_ID_FACTOR = 982451653

# The base64url alphabet used by ark-resolver's check-digit algorithm
# (RFC 4648 Table 2, no padding).
_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def _check_digit(raw_id):
    """Mirrors ark-resolver's base64url_check_digit.calculate_check_digit."""
    length = len(raw_id) + 1
    total = sum(_ALPHABET.index(char) * (length - i) for i, char in enumerate(raw_id))
    char_value = (len(_ALPHABET) - total % len(_ALPHABET)) % len(_ALPHABET)
    return _ALPHABET[char_value]


def _escaped_id_with_check_digit(raw_id):
    # ark-resolver escapes '-' as '=' in URLs, because '-' can be ignored in ARK IDs.
    return (raw_id + _check_digit(raw_id)).replace("-", "=")


DSP_RESOURCE_ID = _escaped_id_with_check_digit(DSP_RAW_RESOURCE_ID)
PHP_RESOURCE_ID = _escaped_id_with_check_digit(PHP_RAW_RESOURCE_ID)


def _load_shortcodes():
    config = configparser.ConfigParser()
    config.read(REGISTRY_PATH)
    return [section for section in config.sections() if section != "DEFAULT"], config


SHORTCODES, REGISTRY = _load_shortcodes()
SHORTCODES_MD_CODES = set(re.findall(r"^\| ([0-9A-Fa-f]{4}) ", SHORTCODES_MD_PATH.read_text(), re.MULTILINE))

# A bare project ARK (no resource ID) for a `UsePhp: true` project always
# 400s on the pinned resolver version: it builds the redirect from
# DSPProjectRedirectUrl but never adds $project_host to the template
# substitution, unlike the non-PHP path. This is a resolver limitation, not
# something a registry entry can be wrong about, so it's excluded here.
PHP_SHORTCODES = [code for code in SHORTCODES if REGISTRY[code].getboolean("UsePhp")]
PROJECT_ARK_SHORTCODES = [code for code in SHORTCODES if code not in PHP_SHORTCODES]


def _dsp_redirect_url(project_id, project_config, resource_id=None, timestamp=None):
    """Mirrors ark_url.py's ArkUrlInfo.to_dsp_redirect_url."""
    template_dict = {
        "project_id": project_id,
        "resource_id": resource_id,
        "timestamp": timestamp,
        "host": project_config["Host"],
    }

    if resource_id is None:
        request_template = Template(project_config["DSPProjectRedirectUrl"])
        template_dict["project_host"] = project_config["ProjectHost"]
    elif timestamp is None:
        request_template = Template(project_config["DSPResourceRedirectUrl"])
    else:
        request_template = Template(project_config["DSPResourceVersionRedirectUrl"])

    resource_iri = Template(project_config["DSPResourceIri"]).substitute(template_dict)
    template_dict["resource_iri"] = quote(resource_iri, safe="")

    project_iri = Template(project_config["DSPProjectIri"]).substitute(template_dict)
    template_dict["project_iri"] = quote(project_iri, safe="")

    return request_template.substitute(template_dict)


def _php_resource_redirect_url(project_config, timestamp=None):
    """Mirrors ark_url.py's ArkUrlInfo.to_php_redirect_url for a resource ARK."""
    resource_int_id = (int(PHP_RAW_RESOURCE_ID, 16) // RESOURCE_INT_ID_FACTOR) - 1
    template_dict = {
        "host": project_config["Host"],
        "resource_int_id": resource_int_id,
        # The PHP server only takes timestamps in the format YYYYMMDD.
        "timestamp": timestamp[0:8] if timestamp else None,
    }
    template_key = "PhpResourceVersionRedirectUrl" if timestamp else "PhpResourceRedirectUrl"
    return Template(project_config[template_key]).substitute(template_dict)


def _resource_redirect_url(project_id, project_config, timestamp=None):
    if project_config.getboolean("UsePhp"):
        return _php_resource_redirect_url(project_config, timestamp)
    return _dsp_redirect_url(project_id, project_config, DSP_RAW_RESOURCE_ID, timestamp)


def _resource_id(project_config):
    return PHP_RESOURCE_ID if project_config.getboolean("UsePhp") else DSP_RESOURCE_ID


def _resource_ark(project_id, resource_id, timestamp=None):
    ark = f"{RESOLVER_URL}/ark:/{NAAN}/1/{project_id}/{resource_id}"
    return f"{ark}.{timestamp}" if timestamp else ark


def _expect_redirect(url, expected_location):
    response = requests.get(url, allow_redirects=False)
    assert response.status_code == 302, f"{url} -> expected 302, got {response.status_code}"
    assert response.headers["location"] == expected_location, url


@pytest.mark.parametrize("shortcode", PROJECT_ARK_SHORTCODES)
def test_project_ark(shortcode):
    project_config = REGISTRY[shortcode]
    expected = _dsp_redirect_url(shortcode, project_config)
    _expect_redirect(f"{RESOLVER_URL}/ark:/{NAAN}/1/{shortcode}", expected)


@pytest.mark.parametrize("shortcode", SHORTCODES)
def test_resource_ark(shortcode):
    project_config = REGISTRY[shortcode]
    expected = _resource_redirect_url(shortcode, project_config)
    _expect_redirect(_resource_ark(shortcode, _resource_id(project_config)), expected)


@pytest.mark.parametrize("shortcode", SHORTCODES)
def test_resource_ark_with_version(shortcode):
    project_config = REGISTRY[shortcode]
    expected = _resource_redirect_url(shortcode, project_config, TIMESTAMP)
    _expect_redirect(_resource_ark(shortcode, _resource_id(project_config), TIMESTAMP), expected)


@pytest.mark.parametrize("shortcode", SHORTCODES)
def test_shortcode_listed_in_shortcodes_md(shortcode):
    assert shortcode in SHORTCODES_MD_CODES, (
        f"{shortcode} is in dasch_ark_registry.ini but has no row in shortcodes.md"
    )
