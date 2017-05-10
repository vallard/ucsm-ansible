#!/usr/bin/env python

from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: cisco_ucs_user
short_description: configures user on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures user on a cisco ucs server
Input Params:
    name:
        description: user name
        required: True
    pwd:
        description: password
        required: False
    clear_pwd_history:
        description: clear password history
        required: False
        choices: ['yes', 'no']
        default: "no"
    pwd_life_time:
        description: password life time
        required: False
        default: "no-password-expire"
    account_status:
        description: account status
        required: False
        choices: ['active', 'inactive']
        default: "active"
    expires:
        description: expires
        required: False
        choices: ['yes', 'no']
        default: "no"
    expiration:
        description: expiration
        required: False
        default: "never"
    enc_pwd_set:
        description: sets password encryption
        required: False
        choices: ['yes', 'no']
        default: "no"
    enc_pwd:
        description: encrypted password
        required: False
    first_name:
        description: first name
        required: False
    last_name:
        description: last name
        required: False
    phone:
        description: phone
        required: False
    email:
        description: email
        required: False
    descr:
        description: description
        required: False

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Rahul Gupta(ragupta4@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_user:
    name: "testuser"
    pwd: "password"
    clear_pwd_history: "yes"
    pwd_life_time: "no-password-expire"
    account_status: "active"
    expires: "no"
    expiration: "never"
    enc_pwd_set: "no"
    enc_pwd: "encrypted_password"
    first_name: "cisco"
    last_name: "cisco"
    phone: "123456789"
    email: "testuser@cisco.com"
    descr: "description"
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                pwd=dict(type='str'),
                clear_pwd_history=dict(type='str', choices=['yes', 'no'], default="no"),
                pwd_life_time=dict(type='str', default="no-password-expire"),
                account_status=dict(type='str', choices=['active', 'inactive'], default="active"),
                expires=dict(type='str', choices=['yes', 'no'], default="no"),
                expiration=dict(type='str', default="never"),
                enc_pwd_set=dict(type='str', choices=['yes', 'no'], default="no"),
                enc_pwd=dict(type='str'),
                first_name=dict(type='str'),
                last_name=dict(type='str'),
                phone=dict(type='str'),
                email=dict(type='str'),
                descr=dict(type='str'),
    )


def _argument_custom():
    return dict(
        state=dict(default="present",
                   choices=['present', 'absent'],
                   type='str'),
    )


def _argument_connection():
    return  dict(
        # UcsHandle
        ucs_server=dict(type='dict'),

        # Ucs server credentials
        ucs_ip=dict(type='str'),
        ucs_username=dict(default="admin", type='str'),
        ucs_password=dict(type='str', no_log=True),
        ucs_port=dict(default=None),
        ucs_secure=dict(default=None),
        ucs_proxy=dict(default=None)
    )


def _ansible_module_create():
    argument_spec = dict()
    argument_spec.update(_argument_mo())
    argument_spec.update(_argument_custom())
    argument_spec.update(_argument_connection())

    return AnsibleModule(argument_spec,
                         supports_check_mode=True)


def _get_mo_params(params):
    from ansible.module_utils.cisco_ucs import UcsConnection
    args = {}
    for key in _argument_mo():
        if params.get(key) is None:
            continue
        args[key] = params.get(key)
    return args


def setup_user(server, module):
    from ucsm_apis.admin.user import user_create
    from ucsm_apis.admin.user import user_delete
    from ucsm_apis.admin.user import user_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = user_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        user_create(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        user_delete(server, mo.name)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_user(server, module)
    except Exception as e:
        err = True
        result["msg"] = "setup error: %s " % str(e)
        result["changed"] = False

    return result, err


def main():
    from ansible.module_utils.cisco_ucs import UcsConnection

    module = _ansible_module_create()
    conn = UcsConnection(module)
    server = conn.login()
    result, err = setup(server, module)
    conn.logout()
    if err:
        module.fail_json(**result)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
