#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_adaptor_policy
short_description: configures adaptor policy on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures adaptor policy on a cisco ucs server
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: "present"
    name:
        version_added: "1.0(1e)"
        description: adaptor policy name
        required: true
    org_dn:
        description: org dn
        required: false
        default: "org-root"
    descr:
        version_added: "1.0(1e)"
        description: description of the policy
        required: false
        default: empty
    vxlan:
        version_added: "1.0(1e)"
        description: should the policy keep trying to mount on failure
        required: false
        choices: ['enabled', 'disabled']
        default: disabled
    rss:
        version_added: "1.0(1e)"
        description: receive side scaling 
        choices: ['enabled', 'disabled']
        default: disabled


requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_adaptor_policy:
    name: KUBAM
    descr: create adaptor policy with vxlan enabled
    vxlan: enabled
    ucs_ip: 192.168.1.1
    ucs_username: admin
    ucs_password: Cisco.123
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                org_dn=dict(type='str', default="org-root"),
                descr=dict(required=False, type='str', default=""),
                vxlan=dict(required=False, 
                                choices=['enabled', 'disabled'],
                                type='str', default="disabled"),
                rss=dict(required=False, 
                                choices=['enabled', 'disabled'],
                                type='str', default="disabled")
    )


def _argument_custom():
    return dict(
        state=dict(default="present",
                   choices=['present', 'absent'],
                   type='str')
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
    argument_spec.update(_argument_connection())
    argument_spec.update(_argument_mo())
    argument_spec.update(_argument_custom())
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

def update_adaptor(args_mo, server):
    from ucsmsdk.mometa.adaptor.AdaptorHostEthIfProfile import AdaptorHostEthIfProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthAdvFilterProfile import AdaptorEthAdvFilterProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthArfsProfile import AdaptorEthArfsProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthCompQueueProfile import AdaptorEthCompQueueProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthFailoverProfile import AdaptorEthFailoverProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthInterruptProfile import AdaptorEthInterruptProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthInterruptScalingProfile import AdaptorEthInterruptScalingProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthNVGREProfile import AdaptorEthNVGREProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthOffloadProfile import AdaptorEthOffloadProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthRecvQueueProfile import AdaptorEthRecvQueueProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthRoCEProfile import AdaptorEthRoCEProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthVxLANProfile import AdaptorEthVxLANProfile
    from ucsmsdk.mometa.adaptor.AdaptorEthWorkQueueProfile import AdaptorEthWorkQueueProfile
    from ucsmsdk.mometa.adaptor.AdaptorExtIpV6RssHashProfile import AdaptorExtIpV6RssHashProfile
    from ucsmsdk.mometa.adaptor.AdaptorIpV4RssHashProfile import AdaptorIpV4RssHashProfile
    from ucsmsdk.mometa.adaptor.AdaptorIpV6RssHashProfile import AdaptorIpV6RssHashProfile
    from ucsmsdk.mometa.adaptor.AdaptorRssProfile import AdaptorRssProfile
    mo = AdaptorHostEthIfProfile(
        parent_mo_or_dn=args_mo['org_dn'],
        name=args_mo['name'],
        descr=args_mo['descr'])
   
    server.add_mo(mo, True) 
    server.commit()

def setup_adaptor_policy(server, module):

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
     
    changed = False
    policy = args_mo['name']    
    mo = server.query_dn(args_mo['org_dn']+"/eth-profile-"+policy)
    exists = False
    if mo:
        exists = True

    if ansible['state'] == 'absent':
        if exists: 
            changed = True
            if not module.check_mode:
                server.remove_mo(mo)
                server.commit()
    else:
        if not exists:
            changed = True
            if not module.check_mode:
                update_adaptor(args_mo, server)

    return changed

def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_adaptor_policy(server, module)
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

