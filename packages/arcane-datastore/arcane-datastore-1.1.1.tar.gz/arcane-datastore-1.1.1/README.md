# Arcane Datastore

This package is based on [google-cloud-datastore](https://pypi.org/project/google-cloud-datastore/).

## Get Started

```sh
pip install arcane-datastore
```

## Example Usage

```python
from arcane import datastore
client = datastore.Client()

entity = client.get_entity('kind-id-here', 1)
```

or

```python
from arcane import datastore

# Import your configs
from configure import Config

client = datastore.Client.from_service_account_json(Config.KEY, project=Config.GCP_PROJECT)

entity = client.get_entity('kind-id-here', 1)
```
