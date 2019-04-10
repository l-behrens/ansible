#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: redis_access_module

short_description: This is my sample module

version_added: "1.0"

description:
    - "This module gives access to an arbitrary redis key/value store"

options:
    get:
        description:
            - get the values to a given list of keys
        required: false
    set:
        description:
            - set key value pairs in redis
        required: false
    dump:
        description:
            - dump the complete key/value store as a dictionary
        required: false

extends_documentation_fragment:
    - database

author:
    - Lars Behrens (l.behrens@openinfrastructure.de)
'''

EXAMPLES = '''
# get key-value entries
- name: get key-value entries for 'a', 'b' and 'c'
  redis_access_module:
    mode: read
    get: ['a', 'b', 'c']

# set a new key-value entry or update an existing one
- name: set key: 'a' to value: 'aval'
  redis_access_module:
    mode: write
    set: {'a': 'aval'}

# dump redis database
- name: get all entries redis holds
  redis_access_module:
    mode: dump
'''

RETURN = '''
get:
    description: A dictionary, that contains the requested key/value entries
    type: dict
set:
    description: A boolean value, that indicates the return code of the operation
    type: boolean
dump:
    description: A dictionary, that represents the complete data in the redis db
'''

from ansible.module_utils.basic import AnsibleModule

try:
    import redis
except ImportError:
    redis_found = False
else:
    redis_found = True

def get_val(r, keys):
    return [r.get(key) for key in keys]

def dump(r):
    res={}
    for key in r.scan_iter():
        res[key] = r.get(key)
    return res

def set_key_val(r, timeout, key_val):
    try:
        with r.lock('my-lock-key', blocking_timeout=timeout) as lock:
            for key in key_val:
                r.set(key, key_val[key])
    except Exeption:
        module.fail_json(msg='Locking redis failed', **result)
def init_redis_client(host='localhost', port=6379, db=0):
    return redis.Redis(host=host, port=port, db=db)

def run_module():
    if not redis_found:
        module.fail_json(msg="the python redis module is required")

    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        port=dict(type='str', required=False, default='6379'),
        host=dict(type='str', required=False, default='127.0.0.1'),
        db=dict(type='int', required=False, default=0),
        set_key_val=dict(type='dict', required=False),
        get_val=dict(type='list', required=False),
        mode=dict(default="get", choices=["get", "set","dump", ]),
        ssl_cert=dict(default=None, type='path'),
        ssl_key=dict(default=None, type='path'),
        ssl_ca=dict(default=None, type='path'),
        connect_timeout=dict(default=5, type='int'),
    )

    r = init_redis_client(
        module.params['host'],
        module.params['port'],
        module.params['db'])

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )


    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.params['mode'] is 'dump':
        result[message] = dump(r)

    elif module.params['mode'] is 'read':
        result[message] = get_val(get_val)

    elif module.params['mode'] is 'write':
        result[message] = 0

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    if module.params['mode'] is 'write':
        result[message] = set_key_val(r, module.params['set_key_val'])
        result[changed] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['name'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():


    run_module()

if __name__ == '__main__':
    main()

