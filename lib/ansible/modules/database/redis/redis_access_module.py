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
    return str({key: r.get(key) for key in keys})

def dump(r):
    res={}
    for key in r.scan_iter():
        res[key] = r.get(key)
    return res

def set_key_val(r, key_val):
    try:
        with r.lock('my-lock-key', blocking_timeout=5) as lock:
            for key in key_val:
                r.set(key, key_val[key])
    except Exeption:
        module.fail_json(msg='Locking redis failed', **result)

def init_redis_client(host='localhost', port=6379, db=0):
    return redis.Redis(host=host, port=port, db=db)

def run_module():

    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        port=dict(type='str', required=False, default='6379'),
        host=dict(type='str', required=False, default='127.0.0.1'),
        db=dict(type='int', required=False, default=0),
        set=dict(type='dict', required=False),
        get=dict(type='list', required=False),
        keys=dict(type='list', required=False),
        mode=dict(default="get", choices=["get", "set","dump", "delete"]),
        ssl_cert=dict(default=None, type='path'),
        ssl_key=dict(default=None, type='path'),
        ssl_ca=dict(default=None, type='path'),
        connect_timeout=dict(default=5, type='int'),
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    if not redis_found:
        module.fail_json(msg="the python redis module is required")

    r = init_redis_client(
        module.params['host'],
        module.params['port'],
        module.params['db'])

    result['message']=module.params['mode']
    if module.params['mode'] == 'dump':
        result['message'] = dump(r)
    elif module.params['mode'] == 'get':
        if not module.params['get']:
            module.fail_json(msg='You must define get: <key> Parameter when mode is get', **result)
        result['message']= get_val(r, module.params['get'])

    elif module.params['mode'] == 'set':
        if not module.params['set']:
            module.fail_json(msg='You must define set: {key: value} Parameter when mode is get', **result)

        result['message'] = "running in checkmode. Set Nothing"

    elif module.params['mode'] == 'delete':
        if not module.params['keys']:
            module.fail_json(msg='You must define keys Parameter when mode is get', **result)

        result['message'] = "running in checkmode. Delete Nothing"

    if module.check_mode:
        return result

    if module.params['mode'] == 'set':
        result['message'] = set_key_val(r, module.params['set'])
        result['changed'] = True

    elif module.params['mode'] == 'delete':
        for i in module.params['keys']:
            ret=r.delete(i)
        result['message'] = 'deleted...'
        result['changed'] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():


    run_module()

if __name__ == '__main__':
    main()

