#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utils for handline kerberos config split across different realms
"""
import os
from collections import defaultdict

from ansible_collections.community.kerberos.plugins.module_utils.kerberos_paths import \
    get_kdc_config_path
from ansible_collections.community.kerberos.plugins.module_utils.kerberos_profile import \
    generate_profile, remove_krb5_realm_config


def write_split_profile(path, data, realm_sections):
    parent_dir = os.path.dirname(path)
    realms_d_path = os.path.join(parent_dir, 'krb5_realms.d')

    global_file, realm_files = generate_split_profile(
        data, realm_sections, realms_d_path
    )

    os.makedirs(realms_d_path, exist_ok=True)

    # Delete unneeded files. This is needed in order to remove
    # files that provide config not in `data`.
    for filename in os.listdir(realms_d_path):
        if filename not in realm_files:
            os.unlink(os.path.join(realms_d_path, filename))

    # TODO - check whether any changes are necessary
    with open(path, "w") as f:
        f.write(global_file)

    for realm_name, content in realm_files.items():
        realm_file_path = os.path.join(realms_d_path, realm_name)

        with open(realm_file_path, "w") as f:
            f.write(content)


def generate_split_profile(data, realm_sections, per_realm_dir):

    global_data = {}
    per_realm_data = defaultdict(lambda: defaultdict(dict))

    # TODO - this code assumes that every key not in certain sections is a realm name. We know this isn't the case.
    for section_name, section in data.items():
        if section_name not in realm_sections:
            global_data[section_name] = section
            continue

        for realm_name, value in section.items():
            per_realm_data[realm_name][section_name][realm_name] = value

    global_profile = generate_profile(global_data) + """

includedir %s
    """ % per_realm_dir

    per_realm_profile = {
        section_name: generate_profile(section_data)
        for section_name, section_data in per_realm_data.items()
    }

    return global_profile, per_realm_profile
