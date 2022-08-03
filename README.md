# pyrena

API wrapper for interacting with Arena QMS.

Pyrena is not associated with or approved by Arena Solutions or PTC.

## Installation

`pip install pyrena`

## Docs

Documentation generated by Pyrena self-introspecting its own code. This goes into more detail than this readme.

```python
import pyrena
pyrena.docs()
```

## Usage

### Create client

```python
import pyrena

client = pyrena.Arena("username", "password")
```

Government users should add the parameter `base_url="https://api.arenagov.com/v1/v1"` during client creation.

### Change users

```python
client.logout()
client.login("different_username", "different_password")
```

### Search

Define an object type and search parameters to get a list of results. Functions equivalently to top bar search on Arena website; however searching based on custom attributes must use the custom attribute GUID. See Arena help documentation on app.bom.com

```python
search_results = client.Listing(client.QualityProcess, number="NCMR-*")
```

### Retrieve specific object

```python
my_change_order = client.Change("object_guid")
```