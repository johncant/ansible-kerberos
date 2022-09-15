#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ansible Kerberos module
"""


from ansible.module_utils.basic import AnsibleModule


def does_kdb_exist(module: AnsibleModule) -> bool:
    """
    Find out if kerberos database exists, using list_mkeys
    """
    retcode, _, _ = module.run_command(["kdb5_util", "list_mkeys"])
    return retcode == 0


def destroy_kdb(module: AnsibleModule) -> bool:
    """
    Destroy kerberos database
    """
    module.run_command(["kdb5_util", "destroy", "-f"], check_rc=True)
    return True


def destroy_kdb_if_exists(module: AnsibleModule) -> bool:
    """
    Destroy kerberos database if it exists
    """
    if does_kdb_exist(module):
        return destroy_kdb(module)
    return False


def create_kdb(
            module: AnsibleModule,
            stash: bool,
            password: str
        ) -> bool:
    """
    Create kdb
    """

    command = ["kdb5_util", "create"]
    if stash:
        command.append("-s")
    command = command + ["-P", password]

    return module.run_command(command, check_rc=True)


def create_kdb_if_not_exists(
            module: AnsibleModule,
            stash: bool,
            password: str
        ) -> bool:
    """
    Create kdb if it does not already exist
    """
    if not does_kdb_exist(module):
        return create_kdb(module, stash, password)
    return False


def main():
    """
    Ansible Kerberos KDB module
    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                type='str',
                default='present',
                choices=['absent', 'present']
            ),
            stash=dict(
                type='bool',
                default=False
            ),
            password=dict(
                type='str',
            )
        ),
        required_if=[
            ['state', 'present', ('password',)],
        ],
        supports_check_mode=True,
    )

    state = module.params['state']
    stash = module.boolean(module.params['stash'])
    password = module.params['password']

    if state == 'absent':
        changed = destroy_kdb_if_exists(module)
    elif state == 'present':
        changed = create_kdb_if_not_exists(module, stash, password)

    module.exit_json(
        changed=changed,
    )


if __name__ == '__main__':
    main()
