DSpace rest client for v7 or above
=====================================

## Using
```
pip install dspace-client
```
on code:
```python
from dspace import DSpaceClient

client = DSpaceClient("https://api7.dspace.org/server/")
client.login("dspacedemo+admin@gmail.com", "dspace")
print(client.get_items())
```

## Goals
- [ ] Implement all endpoints on DSpace Rest Contract
- [ ] Configurable by default
- [ ] All authentication methods
- [ ] Async support

## Features
- Authenticaion using login/password
- Autorefresh token
- Auto XSRF token
- Objects are pydantic friendly not dicts
