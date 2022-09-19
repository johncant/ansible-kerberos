#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Definition of parameters in kerberos config
"""


KDC_GLOBAL_SECTIONS = [
    "kdcdefaults",
    "dbdefaults",
    "logging",
    "otp",
]


KDC_REALM_SECTIONS = [
    "realms",
    "dbmodules",
]


KRB5_GLOBAL_SECTIONS = [
    "libdefaults",
    "appdefaults",
    "plugins",
]


KRB5_REALM_SECTIONS = [
    "realms",
    "domain_realm",
    "capaths",
    "appdefaults",
]
