# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane']

package_data = \
{'': ['*']}

install_requires = \
['arcane-core>=1.6.0,<2.0.0',
 'backoff>=1.10.0,<2.0.0',
 'google-cloud-storage>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'arcane-storage',
    'version': '0.4.1',
    'description': '',
    'long_description': "# Arcane Storage\n\nThis package is base on [google-cloud-storage](https://pypi.org/project/google-cloud-storage/).\n\n## Get Started\n\n```sh\npip install arcane-storage\n```\n\n## Example Usage\n\n```python\nfrom arcane import storage\nclient = storage.Client()\n\nblobs = client.list_blobs('bucket-id-here')\n```\n\nor\n\n```python\nfrom arcane import storage\n\n# Import your configs\nfrom configure import Config\n\nclient = storage.Client.from_service_account_json(Config.KEY, project=Config.GCP_PROJECT)\n\nblobs = client.list_blobs('bucket-id-here')\n```\n",
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
