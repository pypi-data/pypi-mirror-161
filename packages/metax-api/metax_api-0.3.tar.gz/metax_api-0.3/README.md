# Leviathan Metax python3 API v2.0 

## API

### module structure

```
metax/
├── api.py
├── db
│    ├── __main__.py
│    ├── __init__.py
│    ├── friends.py
│    ├── get.py
│    ├── delete.py
│    ├── keys.py
│    ├── listener.py
│    ├── copy.py
│    ├── metax_base.py
│    ├── metax_info.py
│    ├── pair.py
│    ├── peers.py
│    ├── save.py
│    ├── send_to.py
│    ├── share.py
│    └── update.py
│
├── __main__.py
├── __init__.py
├── errors.py
├── request.py
├── requirements.txt
└── types.py
```

### Methods
* is valid uuid        - `metax.db.metax_base:Base::is_valid_uuid`
* validate             - `metax.db.metax_base:Base::validate`
* copy                 - `metax.db.copy:Copy::copy`
* delete               - `metax.db.delete:Delete::delete`
* add friend           - `metax.db.friends:Friends::add_friend`
* get friend list      - `metax.db.copy:Friends::get_friends_list`
* get                  - `metax.db.get:Get::get`
* get user keys        - `metax.db.keys:Keys::get_user_keys`
* get user public key  - `metax.db.keys:Keys::get_user_public_key`
* regenerate user key  - `metax.db.keys:Keys::regenerate_user_key`
* regiseter listeners  - `metax.db.listeners:Listeners::register_listener`
* unregister listeners - `metax.db.listeners:Listeners::unregister_listener`
* listeners            - `metax.db.listeners:Listeners::listeners`
* set metax info       - `metax.db.metax_info:MetaxInfo::set_metax_info`
* get metax info       - `metax.db.metax_info:MetaxInfo::get_metax_info`
* dump user info       - `metax.db.metax_info:MetaxInfo::dump_user_info`
* start_pairing        - `metax.db.pair:Pair::start_pairing`
* cancel_pairing       - `metax.db.pair:Pair::cancel_pairing`
* get pairing peers    - `metax.db.pair:Pair::get_pairing_peers`
* peers                - `metax.db.peers:Peers::peers`
* reconnect_to_peers   - `metax.db.peers:Peers::reconnect_to_peers`
* save                 - `metax.db.save:Save:save`
* send to              - `metax.db.send_to:SendTo::send_to`
* share                - `metax.db.share.Share::share`
* accept_share         - `metax.db.share.Share::accept_share`
* update               - `metax.db.update:Update::update`
* metax                - `metax.api.metax` - `metax::Metax`
* crud                 - `metax.api.crud` - `metax::CRUD`

### Statements
* NODE         - `metax.types.NODE`
* FORM         - `metax.types.FORM`
* EXPIRE       - `metax.types.EXPIRE`
* ENCRYPT      - `metax.types.ENCRYPT`
* ENCRYPTED    - `metax.types.ENCRYPTED`
* NO_ENCRYPTED - `metax.types.NO_ENCRYPTED`
* SECURE       - `metax.types.SECURE`
* NO_SECURE    - `metax.types.NO_SECURE`
* GET          - `metax.types.GET`
* POST         - `metax.types.POST`
* UPDATE       - `metax.types.UPDATE`
* DELETE       - `metax.types.DELETE`
* ANY          - `metax.types.ANY`


### Return Types
---
1. Event - `metax.db.listeners:Event`:
	1. Statements:
		1. type   - **str** - event type
		2. target - **str** - file listener uuid in other events is a none
		3. event  - **str** - raw event received from server
	2. Methods:
		1. This Class Without any method

---
2. Response - `metax.request:Response`:
	1. Statements:
		1. status        - **int** - Status code of request
		2. data          - **byte** - response from server
		3. as_string     - **str** - unicode decoded data response from server
		4. success       - **bool** - return true if request is success
		5. raw           - **get** - resuqest/response data
	2. Methods:
		1. json          - `return dict object of response content`
		2. text          - `return the string object od response content`


### Usage
---
#### `is_valid_uuid: `

```python
from metax.db.metax_base import Base # all other reqest types extend Base class methods and statements
from metax.types import NO_SECURE

base = Base('localhost', 8001, NO_SECURE)

uuid  = "066177b7-58ef-4371-8784-6af2fe3802c0"  # valid uuid
uuid2 = "066177b7-58ef-4371-8784-6aaf2fe3802c0" # length of last segment is large than must

print( base.is_valid_uuid(uuid) ) # true
print( base.is_valid_uuid(uuid2) ) # false
```
#### `validate: `

```python
from metax.db.metax_base import Base # all other reqest types extend Base class methods and statements
from metax.types import NO_SECURE

base = Base('localhost', 8001, NO_SECURE)

resp1  = "{\"uuid\":\"066177b7-58ef-4371-8784-6af2fe3802c0\"}"  # valid response
resp2  = "{\"error\":\"Getting file failed\"}" # invalid response

print( base.is_valid_uuid(resp1) ) # Nothing
print( base.is_valid_uuid(resp2) ) # Error type` metax.errors.GettingFileFiledError
```
#### `copy: `

```python
from metax.db.copy import Copy
from metax.types import NO_SECURE

base = Copy('localhost', 8001, NO_SECURE)

uuid  = "066177b7-58ef-4371-8784-6af2fe3802c0"  # valid uuid

print( base.copy(uuid) ) # return a new uuid or error
```
#### `delete: `

```python
from metax.db.delete import Delete
from metax.types import NO_SECURE

base = Delete('localhost', 8001, NO_SECURE)

uuid  = "066177b7-58ef-4371-8784-6af2fe3802c0"  # valid uuid

print( base.delete(uuid) ) # return deleted uuid or error
```
#### `add friend: `

```python
from metax.db.friends import Friends
from metax.types import NO_SECURE

base = Friends('localhost', 8001, NO_SECURE)

friend_key = "PUBLIC_RSA_KEY"

print( base.add_friend(friend_key) )
```
#### `get friend list: `

```python
from metax.db.friends import Friends
from metax.types import NO_SECURE

base = Friends('localhost', 8001, NO_SECURE)

print( base.get_friends_list() )
```
#### `get: `

```python
from metax.db.get import Get
from metax.types import NO_SECURE

base = Get('localhost', 8001, NO_SECURE)

uuid  = "066177b7-58ef-4371-8784-6af2fe3802c0"  # valid uuid

print( base.get(uuid) )
```
#### `get user key: `

```python
from metax.db.keys import Keys
from metax.types import NO_SECURE

base = Keys('localhost', 8001, NO_SECURE)

print( base.get_user_keys() )
```
#### `get user public key: `

```python
from metax.db.keys import Keys
from metax.types import NO_SECURE

base = Keys('localhost', 8001, NO_SECURE)

print( base.get_user_public_key() )
```
#### `regenerate user key: `

```python
from metax.db.keys import Keys
from metax.types import NO_SECURE

base = Keys('localhost', 8001, NO_SECURE)

print( base.regenerate_user_key() )
```
#### `regiseter listeners: `

```python
from metax.db.listeners import Listeners
from metax.types import NO_SECURE

def cb(event):
	print(event.type)

base = Listeners('localhost', 8001, NO_SECURE)

uuid  = "066177b7-58ef-4371-8784-6af2fe3802c0"

print( base.register_listener(uuid, cb) )
```
#### `set metax info: `

```python
from metax.db.metax_info import MetaxInfo
from metax.types import NO_SECURE

base = MetaxInfo('localhost', 8001, NO_SECURE)

uuid  = "066177b7-58ef-4371-8784-6af2fe3802c0"

print( base.set_metax_info(uuid) )
```
#### `get metax info: `

```python
from metax.db.metax_info import MetaxInfo
from metax.types import NO_SECURE

base = MetaxInfo('localhost', 8001, NO_SECURE)

print( base.get_metax_info() )
```
#### `dump user info: `

```python
from metax.db.metax_info import MetaxInfo
from metax.types import NO_SECURE

base = MetaxInfo('localhost', 8001, NO_SECURE)

print( base.dump_user_info() )
```
#### `start pairing: `

```python
from metax.db.pair import Pair
from metax.types import NO_SECURE

base = Pair('localhost', 8001, NO_SECURE)

print( base.start_pairing(timeout=5) )
```
#### `cancel pairing: `

```python
from metax.db.pair import Pair
from metax.types import NO_SECURE

base = Pair('localhost', 8001, NO_SECURE)

print( base.cancel_pairing() )
```
#### `get pairing peers: `

```python
from metax.db.pair import Pair
from metax.types import NO_SECURE

base = Pair('localhost', 8001, NO_SECURE)

print( base.get_pairing_peers() )
```
#### `peers: `

```python
from metax.db.peers import Peers
from metax.types import NO_SECURE

base = Peers('localhost', 8001, NO_SECURE)

print( base.peers() )
```
#### `reconnect to peers: `

```python
from metax.db.peers import Peers
from metax.types import NO_SECURE

base = Peers('localhost', 8001, NO_SECURE)

print( base.reconnect_to_peers() )
```
#### `save: `

```python
from metax.db.save import Save
from metax.types import NO_SECURE

base = Save('localhost', 8001, NO_SECURE)

print( base.save("data ot nothing to create empty file") )
```
#### `send to: `

```python
from metax.db.send_to import SendTo
from metax.types import NO_SECURE

base = SendTo('localhost', 8001, NO_SECURE)

print( base.send_to("PUBLIC_KEY", "DATA TO SEND") )
```
#### `share: `

```python
from metax.db.share import Share
from metax.types import NO_SECURE

base = Share('localhost', 8001, NO_SECURE)

print( base.send_to("UUID", "PUBLIC_KEY") )
```
#### `accept share: `

```python
from metax.db.share import Share
from metax.types import NO_SECURE

base = Share('localhost', 8001, NO_SECURE)

print( base.accept_share("UUID", "PUBLIC_KEY", "IV") )
```
#### `update: `

```python
from metax.db.update import Update
from metax.types import NO_SECURE

base = Update('localhost', 8001, NO_SECURE)

print( base.update("UUID", "New Content") )
```
#### `Metax: `

```python
from metax import Metax
from metax.types import NO_SECURE

base = Metax('localhost', 8001, NO_SECURE)

print( base.save("Data") ) # new file uuid
print( base.update("UUID", "New Content").success)
print( base.get("UUID") ) # resposne

# Metax class Extend all classes for request to metax web api
```
#### `CRUD: `

```python
from metax import CRUD
from metax.types import NO_SECURE

base = CRUD('localhost', 8001, NO_SECURE)

print( base.save("Data") ) # new file uuid
print( base.update("UUID", "New Content").success)
print( base.get("UUID") ) # resposne
print( base.delete("UUID") ) # resposne

# CRUD class extends only (C)reate (R)ead (D)elete (U)pdate requests to metax web api
```

## Requirements

1. Python 3.7+
2. Pip Packages
	1. requests
	2. websocket-client
	3. commands to install all in ubuntu:
		1. sudo apt install python3 python3-dev python3-pip
		2. python3 -m pip install requirements.txt # or
		3. python3 -m pip install requests websocket-client==0.37.0

## Other

### Definition 'headers'
---
#### Copy
```python
class Copy(Base):
	def __init__(self, *args, **kwargs):...

	def copy(self, uuid:str, **query_params:dict) -> Response:...
```
#### Delete
```python
class Delete(Base):
	def __init__(self, *args, **kwargs):...

	def delete(self, uuid:str, **query_params:dict) -> Response:...
```
#### Friends
```python
class Friends(Base):
	def __init__(self, *args, **kwargs):...

	def add_friend(self, key:str, username:str, **query_params:dict) -> Response:...

	def get_friends_list(self, **query_params:dict) -> Response:...
```
#### Get
```python
class Get(Base):
	def __init__(self, *args, **kwargs):...

	def get(self, uuid:str, **query_params:dict) -> Response:...
```
#### Keys
```python
class Keys(Base):
	def __init__(self, *args, **kwargs):...

	def get_user_keys(self, **query_params:dict) -> Response:...

	def get_user_public_key(self, **query_params:dict) -> Response:...

	def regenerate_user_key(self, **query_params:dict) -> Response:...
```
#### Listeners
```python
class Listener(Base):
	__listeners = []
	any_event = lambda *a, **k:...

	def __init__(self, *args, **kwargs):...

	def listeners(self) -> list:...

	def register_listener(self, uuid:str, callback:callable, type_:str=ANY,  **query_params:dict) -> Response:...

	def unregister_listener(self, uuid:str, **query_params:dict) -> Response:...

	def init_registers(self, *args:list, **kwargs:dict) -> None:

	def event(self, response:self) -> None:...

	def on_ws_message(self, socket:WebSocketApp, message:str) -> None:...
```
#### Base
```python
class Base:
	def __init__(self, host:str, port:int, secure:bool=False):...

	def validate(self, response:Response) -> None:...

	def is_valid_uuid(self, uuid:str) -> bool:...
```
#### Metax Info
```python
class MetaxInfo(Base):
	def __init__(self, *args:list, **kwargs:dict) :...

	def set_metax_info(self, uuid:str, **query_params:dict) -> Response:...

	def get_metax_info(self, **query_params:dict) -> Response:...

	def dump_user_info(self, **query_params:dict) -> Response:...
```
#### Pair
```python
class Pair(Base):
	def __init__(self, *args, **kwargs):...

	def start_pairing(self, timeout:int, **query_params:dict) -> Response:...

	def cancel_pairing(self, **query_params:dict) -> Response:...

	def get_pairing_peers(self, **query_params:dict) -> Response:...
```
#### Peers
```python
class Peers(Base):
	def __init__(self, *args, **kwargs):...

	def peers(self, **query_params:dict) -> Response:...

	def reconnect_to_peers(self, **query_params:dict) -> Response:...
```
#### Save 
```python
class Save(Base):
	def __init__(self, *args, **kwargs):...

	def save(self, data:str='', type:str=NODE, **query_params:dict) -> Response:...
```
#### SendTo
```python
class SendTo(Base):
	def __init__(self, *args, **kwargs):...

	def send_to(self, key:str, data:str, **query_params:dict) -> Response:...
```
#### Share
```python
class Share(Base):
	def __init__(self, *args, **kwargs):...

	def share(self, uuid:str, key:str, **query_params:dict) -> Response:...

	def accept_share(self, uuid:str, key:str, iv:str, **query_params:dict) -> Response:...
```
#### Update
```python
class Update(Base):
	def __init__(self, *args, **kwargs):...

	def update(self, uuid:str, data:str, type:str=NODE, **query_params:dict) -> Response:...
```
