#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utils for determining paths of kerberos config
"""


def get_kdc_config_path(module):
    """
    Returns the path for the KDC config
    """
    # TODO - determine location of kdc config
    return "/etc/krb5kdc/kdc.conf"


def get_krb5_config_path(module):
    """
    Returns the path for the KDC config
    """
    # TODO - determine location of krb5 config
    return "/etc/krb5.conf"


