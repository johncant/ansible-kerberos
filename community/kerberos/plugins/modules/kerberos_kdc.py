#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ansible module for managing KDC configuration
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.kerberos.plugins.module_utils.kerberos_profile import merge_krb5_profiles, generate_profile, parse_profile


KDC_SECTIONS = [
    "kdcdefaults",
    "dbdefaults",
    "logging",
    "otp",
]


def get_kdc_config_path(module):
    """
    Returns the path for the KDC config
    """
    # TODO - determine location of kdc config
    return "/etc/krb5kdc/kdc.conf"


def destroy_kdc_config_if_exists(module):
    """
    Destroys KDC config
    """
    path = get_kdc_config_path(module)

    if os.path.exists(path):
        os.unlink(path)

    return True



def write_krb5_kdc_config(module, path, data):
    # TODO - write includedir system

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write(generate_profile(data))


def create_or_modify_kdc_config(module, updates):
    path = get_kdc_config_path(module)

    if os.path.exists(path):
        existing_config = parse_profile(path)
    else:
        existing_config = {}

    new_config = merge_krb5_profiles(existing_config, updates)

    write_krb5_kdc_config(module, path, new_config)

    return True


def main():
    """
    Ansible Kerberos KDC module
    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                type='str',
                default='present',
                choices=['absent', 'present']
            ),
            dbdefaults=dict(
                type='dict',
            ),
            kdcdefaults=dict(
                type='dict',
            ),
            logging=dict(
                type='dict',
            ),
            otp=dict(
                type='dict',
            ),
        ),
        supports_check_mode=True,
    )

    state = module.params['state']

    kdc_options = {
        k: module.params[k] for k in KDC_SECTIONS
        if module.params[k]
    }

    if state == 'absent':
        changed = destroy_kdc_config_if_exists(module)
    else:
        changed = create_or_modify_kdc_config(
            module,
            kdc_options,
        )

    module.exit_json(
        changed=changed,
    )


if __name__ == '__main__':
    main()
