#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ansible module for managing krb5 and kdc realm configuration
"""

import os

from ansible.module_utils.basic import AnsibleModule
# from ansible_collections.community.kerberos.plugins.module_utils.kerberos_profile import 
from ansible_collections.community.kerberos.plugins.module_utils.kerberos_parameters import KDC_REALM_SECTIONS, KRB5_REALM_SECTIONS, KDC_GLOBAL_SECTIONS, KRB5_GLOBAL_SECTIONS
from ansible_collections.community.kerberos.plugins.module_utils.kerberos_split_profile import write_split_profile
from ansible_collections.community.kerberos.plugins.module_utils.kerberos_profile import parse_profile, merge_krb5_profiles, remove_krb5_realm_config
from ansible_collections.community.kerberos.plugins.module_utils.kerberos_paths import get_kdc_config_path, get_krb5_config_path


def modify_krb5_realm_config(
            existing_config,
            realm_name,
            global_section_names,
            realm_section_names,
            updates,
        ):

    new_config = {}

    realm_section_updates = {
        section_name: {
            realm_name: section_realm_data
        }
        for section_name, section_realm_data in updates.items()
    }

    return merge_krb5_profiles(
        existing_config,
        realm_section_updates,
        on_conflict="update"
    )


def create_or_modify_realm_profile(
            module,
            realm_name,
            existing_config_path,
            global_section_names,
            realm_section_names,
            updates,
        ):

    if os.path.exists(existing_config_path):
        existing_config = parse_profile(existing_config_path)
    else:
        existing_config = {}

    new_config = modify_krb5_realm_config(existing_config, realm_name, global_section_names, realm_section_names, updates)

    write_split_profile(existing_config_path, new_config, realm_section_names)

    return True


def destroy_realm_profile(
            module,
            realm_name,
            existing_config_path,
            global_section_names,
            realm_section_names,
        ):

    if os.path.exists(existing_config_path):
        existing_config = parse_profile(existing_config_path)
    else:
        existing_config = {}

    new_config = remove_krb5_realm_config(existing_config, realm_name, global_section_names, realm_section_names)

    write_split_profile(existing_config_path, new_config, realm_section_names)

    return True


def create_or_modify_realm_config(module, realm_name, kdc_config, krb5_config):
    kdc_config_path = get_kdc_config_path(module)
    krb5_config_path = get_krb5_config_path(module)

    if kdc_config is not None:
        changed_kdc = create_or_modify_realm_profile(
            module, realm_name, kdc_config_path,
            KDC_GLOBAL_SECTIONS, KDC_REALM_SECTIONS,
            kdc_config
        )

    if krb5_config is not None:
        changed_krb5 = create_or_modify_realm_profile(
            module, realm_name, krb5_config_path,
            KRB5_GLOBAL_SECTIONS, KRB5_REALM_SECTIONS,
            krb5_config
        )

    return changed_kdc or changed_krb5


def destroy_realm_configs_if_exists(module, realm_name):
    kdc_config_path = get_kdc_config_path(module)
    krb5_config_path = get_krb5_config_path(module)

    if os.path.exists(kdc_config_path):
        changed_kdc = destroy_realm_profile(
            module, realm_name, kdc_config_path,
            KDC_GLOBAL_SECTIONS, KDC_REALM_SECTIONS
        )

    if os.path.exists(krb5_config_path):
        changed_krb5 = destroy_realm_profile(
            module, realm_name, krb5_config_path,
            KRB5_GLOBAL_SECTIONS, KRB5_REALM_SECTIONS
        )

    return changed_kdc or changed_krb5


def main():
    """
    Ansible Kerberos KDC module
    """
    # TODO - add option to purge existing config
    # TODO - add option to purge other realms
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                type='str',
                default='present',
                choices=['absent', 'present']
            ),
            name=dict(
                type=str
            ),
            kdc_config=dict(
                type='dict',
            ),
            krb5_config=dict(
                type='dict',
            ),
        ),
        supports_check_mode=True,
    )

    state = module.params['state']

    realm_name = module.params['name']

    kdc_options = module.params['kdc_config']
    krb5_options = module.params['krb5_config']

    if state == 'absent':
        changed = destroy_realm_configs_if_exists(module, realm_name)
    else:
        changed = create_or_modify_realm_config(
            module,
            realm_name,
            kdc_options,
            krb5_options,
        )
#    print("Finished with success")

    module.exit_json(
        changed=changed,
    )


if __name__ == '__main__':
    main()
