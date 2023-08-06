# Arcane Storage

This package is base on [google-cloud-storage](https://pypi.org/project/google-cloud-storage/).

## Get Started

```sh
pip install arcane-storage
```

## Example Usage

```python
from arcane import storage
client = storage.Client()

blobs = client.list_blobs('bucket-id-here')
```

or

```python
from arcane import storage

# Import your configs
from configure import Config

client = storage.Client.from_service_account_json(Config.KEY, project=Config.GCP_PROJECT)

blobs = client.list_blobs('bucket-id-here')
```
