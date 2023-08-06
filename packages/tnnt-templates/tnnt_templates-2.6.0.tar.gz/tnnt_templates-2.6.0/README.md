# Terra Nanotech Auth Templates

[![Version](https://img.shields.io/pypi/v/tnnt-templates?label=release)](https://pypi.org/project/tnnt-templates/)
[![GitHub license](https://img.shields.io/github/license/terra-nanotech/tn-nt-auth-templates)](https://github.com/terra-nanotech/tn-nt-auth-templates/blob/master/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/tnnt-templates)](https://pypi.org/project/tnnt-templates/)
[![Django](https://img.shields.io/pypi/djversions/tnnt-templates?label=django)](https://pypi.org/project/tnnt-templates/)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)
[![Discord](https://img.shields.io/discord/790364535294132234?label=discord)](https://discord.gg/zmh52wnfvM)
[![Checks](https://github.com/terra-nanotech/tn-nt-auth-templates/actions/workflows/automated-checks.yml/badge.svg)](https://github.com/terra-nanotech/tn-nt-auth-templates/actions/workflows/automated-checks.yml)
[![codecov](https://codecov.io/gh/terra-nanotech/tn-nt-auth-templates/branch/master/graph/badge.svg?token=4JLA8CXJ64)](https://codecov.io/gh/terra-nanotech/tn-nt-auth-templates)


Template Overrides for Alliance Auth

![TN-NT Auth Template](https://raw.githubusercontent.com/terra-nanotech/tn-nt-auth-templates/master/tnnt_templates/images/tnnt-template.jpg)


```shell
pip install tnnt-templates
```

In `local.py` right after `INSTALLED_APPS`:

```python
# TN-NT Auth Templates
INSTALLED_APPS.insert(0, "tnnt_templates")

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "tnnt_templates.context_processors.tnnt_settings"
)

TNNT_TEMPLATE_ENTITY_ID = 8154711  #  replace with your corp/alliance ID
TNNT_TEMPLATE_ENTITY_TYPE = "corporation"  # default: "alliance"
TNNT_TEMPLATE_ENTITY_NAME = "My Awesome Corp/Alliance"  # your corp/alliance name

# the URLs are shown in the user menu
TNNT_TEMPLATE_URLS_OWN_WEBSITES = [
    {
        "name": "Website",
        "url": "https://webseite.com/",
        "new_tab": True,
    },
    {
        "name": "Forums",
        "url": "https://forum.website.com/",
        "new_tab": True,
    },
]

TNNT_TEMPLATE_URLS_OTHER_WEBSITES = [
    {
        "name": "Website",
        "url": "https://website.com/",
        "new_tab": True,
    },
]
```

**Important**

If you are using `AA-GDPR`, the template stuff needs to be **after** the `AA_GDPR`
entry, like this:

```python
# GDPR Compliance
INSTALLED_APPS.insert(0, "aagdpr")
AVOID_CDN = True


# TN-NT Auth Templates
INSTALLED_APPS.insert(0, "tnnt_templates")
```
