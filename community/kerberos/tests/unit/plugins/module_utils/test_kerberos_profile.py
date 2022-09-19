#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for manipulation of kerberos profiles
"""

import pytest
from insights.core.context import Context
from insights.parsers.krb5 import Krb5Configuration

import ansible_collections.community.kerberos.plugins.module_utils.\
    kerberos_profile as kp


def test_parse_kerberos_profile():
    """
    Test parsing kerberos profile with include and includedir directives
    """
    path = "tests/data/kerberos_profile/base/kdc.conf"

    data = kp.parse_profile(path)

    assert 'libdefaults' in data
    assert 's2' in data

    assert 'INCLUDE1' in data['libdefaults']
    assert 'INCLUDE2' in data['libdefaults']


def test_generate_kerberos_profile_roundtrip():
    """
    Test generation of kerberos profile.
    """
    data = {
        'libdefaults': {
            'foo': {
                'bar': 'baz'
            }
        }
    }

    krb5_profile = kp.generate_profile(data)

    assert type(krb5_profile) is str

    parsed_config = Krb5Configuration(
        context=Context(
            content=krb5_profile.splitlines()
        )
    ).data

    print(krb5_profile)
    print(parsed_config)
    print(data)

    assert parsed_config == data


def test_merge_krb5_profiles_updates():
    conf1 = {
        'logging': {
            'debug': True
        }
    }

    conf2 = {
        'logging': {
            'debug': False
        }
    }

    conf_merged = kp.merge_krb5_profiles(conf1, conf2, on_conflict='update')

    assert conf_merged['logging']['debug'] is False


def test_merge_krb5_profiles_disallows_conflicts():
    conf1 = {
        'logging': {
            'debug': True
        }
    }

    conf2 = {
        'logging': {
            'debug': False
        }
    }

    with pytest.raises(kp.Krb5ProfileMergeConflictError):
        kp.merge_krb5_profiles(conf1, conf2, on_conflict='error')
