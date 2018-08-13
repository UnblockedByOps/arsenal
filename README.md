# Arsenal

Overview
------

Arsenal is an operations database for tracking the lifecycle of physical and virtual servers in an infrastructure. An agent runs on all servers that registers to an api periodically (currently every 3 hours). Some of arsenal's key features include:

* Regex search for nodes filtered by name, operating system, hardware type, status, and more.
* Setting status on nodes. Useful for keying things like monitoring and software deployment off of.
* Create and assign node groups (puppet node classification). 
* Add tags to nodes and node groups (business unit cost tracking)
* Hypervisor to guest vm mappings. Know what hypervisor contains what vms, and vice versa.
* Network switch port and IP address information for physical hosts.

All with audit tracking to see what changed when, and by whom.

Installation
------

TBD. Need to get control of the python package on pypi.

Development
------

Follow these steps to set up a local development environment for Arsenal (assumes you have ~/git and ~/venvs folders, adjust accordingly if not.)

```bash
cd ~/git
git clone git@github.rp-core.com:Devops/arsenal.git
```

### Install Mysql DB

Install a local mysql db and connect to it as root.

```sql
create database arsenal;
CREATE USER 'readwrite'@'localhost' IDENTIFIED BY '__PASSWORD__';
CREATE USER 'readwrite'@'%' IDENTIFIED BY '__PASSWORD__';
GRANT ALL PRIVILEGES ON arsenal.* TO 'readwrite'@'%';
GRANT ALL PRIVILEGES ON arsenal.* TO 'readwrite'@'localhost';
FLUSH PRIVILEGES;
```

Import the schema and data.

```bash
mysql -u root -p < ~/git/arsenal/server/arsenalweb/db/arsenal-schema.sql
mysql -u root -p < ~/git/arsenal/server/arsenalweb/db/arsenal-data.sql
```

### Install the webapp

Create a virtualenv and install the requirements.

```bash
cd ~/venvs
virtualenv arsenalweb
. arsenalweb/bin/activate
mkdir arsenalweb/conf
mkdir arsenalweb/sconf
pip install -r ~/git/arsenal/server/requirements.txt --global-option=build_ext --global-option="-I$(xcrun --show-sdk-path)/usr/include/sasl"
```

Copy sample configs and install Arsenal.

```bash
cd ~/git/arsenal/server
cp conf/arsenal-web-dev.ini ~/venvs/arsenalweb/conf/arsenal-web.ini
cp conf/arsenal_secrets.ini ~/venvs/arsenalweb/sconf/
 
python setup.py develop
```

Update configs to point at your local DB.

```bash
cd ~/venvs/arsenalweb
vi conf/arsenal-web.ini
```

and change the ~ to the absolute path on this line (python can't resolve it):

```python
arsenal.secrets_file = ~/venvs/arsenalweb/sconf/arsenal_secrets.ini
```

save & exit


```bash
vi sconf/arsenal_secrets.ini
```

Add your mysql username and password

Run the webserver.

```bash
pserve --reload conf/*.ini
```

You should now be able to access your local Arsenal install in your web browser:

http://0.0.0.0:8281
 
You can make changes directly in your ~/git/arsenal repo folder and the web server will pick them up and reload.


API
------

This outlines how to use the API directly instead of the command line client. All examples are python.

## Authentication

```python
>>> import json
>>> import requests
>>>
>>> def login(arsenal_server):
...     '''Log in to the arsenal sever.'''
...     payload = {
...         'login': 'kaboom',
...         'password': 'password',
...         'form.submitted': '',
...         'return_url': '',
...     }
...     session = requests.Session()
...     url = '{0}/login'.format(arsenal_server)
...     session.post(url, data=payload)
...     return session
...
>>> arsenal_server = 'https://arsenal'
>>> session = login(arsenal_server)
```

## Querying

### By Name

To search for a server with the name 'testserver.internal' and a status of 'setup' you would do the following:

```python
>>> headers = {'Content-Type': 'application/json'}
>>> url = '{0}/api/nodes'.format(arsenal_server)
>>> payload = {
...     'name': 'testserver.internal',
...     'status': 'setup',
...     'fields': 'status'
... }
>>> resp = session.get(url, headers=headers, params=payload)
>>> print json.dumps(resp.json(), sort_keys=True, indent=2)
{
  "meta": {
    "result_count": 1,
    "total": 1
  },
  "results": [
    {
      "id": 33400,
      "name": "testserver.internal",
      "status": {
        "id": 2,
        "name": "setup"
      },
      "unique_id": "423fbbd3-6793-4788-ed19-924beafbcbc0"
    }
  ]
}
>>>
```

To search for a node by its unique_id:

```python
>>> headers = {'Content-Type': 'application/json'}
>>> url = '{0}/api/nodes'.format(arsenal_server)
>>> payload = {
...     'unique_id': '423fbbd3-6793-4788-ed19-924beafbcbc0',
...     'status': 'setup',
...     'fields': 'status'
... }
>>> resp = session.get(url, headers=headers, params=payload)
>>> print json.dumps(resp.json(), sort_keys=True, indent=2)
{
  "meta": {
    "result_count": 1,
    "total": 1
  },
  "results": [
    {
      "id": 33400,
      "name": "testserver.internal",
      "status": {
        "id": 2,
        "name": "setup"
      },
      "unique_id": "423fbbd3-6793-4788-ed19-924beafbcbc0"
    }
  ]
}
>>>
```

### NOTES

* Searching does not require authentication. The session is used in these examples for consistency with the rest.
* You can determine the server's unique_id from the server itself by running the following client command as root:

```bash
[root@testserver.internal ~]# arsenal uid
unique_id: 423FBBD3-6793-4788-ED19-924BEAFBCBC0
[root@testserver.internal ~]#
```

## Making changes

### Changing  status

To change the status of that server from 'setup' to 'inservice', first we have to get the id of the status you wish to set:

```python
>>> url = '{0}/api/statuses'.format(arsenal_server)
>>> payload = {'name': 'inservice'}
>>> resp = session.get(url, headers=headers, params=payload)
>>> print json.dumps(resp.json(), sort_keys=True, indent=2)
{
  "meta": {
    "result_count": 1,
    "total": 1
  },
  "results": [
    {
      "id": 3,
      "name": "inservice"
    }
  ]
}
>>>
```

So in this case the 'inservice' status id is 3. Next, append the node id to the status endpoint:

```python
>>> url = '{0}/api/statuses/3/nodes'.format(arsenal_server)
>>> payload = {'nodes': [33400]}
>>> resp = session.put(url, headers=headers, json=payload)
>>> print json.dumps(resp.json(), sort_keys=True, indent=2)
{
  "message": "Command Successful",
  "response": {
    "inservice": [
      "testserver.internal"
    ]
  },
  "status": "200"
}
```

The payload must always be a list of one or more node IDs.

### Unauthorized

If you try to make a change to something you are not authorized to do:

```python
>>> url = '{0}/api/node_groups/360/nodes'.format(arsenal_server)
>>> payload = {'nodes': [33400]}
>>> resp = session.put(url, headers=headers, json=payload)
>>> print json.dumps(resp.json(), sort_keys=True, indent=2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Library/Python/2.7/site-packages/requests/models.py", line 819, in json
    return json.loads(self.text, **kwargs)
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/json/__init__.py", line 338, in loads
    return _default_decoder.decode(s)
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/json/decoder.py", line 366, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/json/decoder.py", line 384, in raw_decode
    raise ValueError("No JSON object could be decoded")
ValueError: No JSON object could be decoded
>>> print resp.status_code
403
>>>
```

## Todo list

### API

* Need ability to set variables for puppet ENC at all levels.

### UI

* Currently no ability to create or edit anything via the UI (done via the client).
* No ability to manage users/groups/passwords etc via the UI (done via direct db insert).
* Need localstorage solution for saving what columns a user has chosen to show/hide on each page.

### CLI

* formatting of output needs a lot of help.
