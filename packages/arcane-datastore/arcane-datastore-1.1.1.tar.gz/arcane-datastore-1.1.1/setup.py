# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane', 'arcane.datastore']

package_data = \
{'': ['*']}

install_requires = \
['arcane-core>=1.6.0,<2.0.0',
 'backoff>=1.10.0,<2.0.0',
 'google-cloud-datastore>=2.5.1,<3.0.0']

setup_kwargs = {
    'name': 'arcane-datastore',
    'version': '1.1.1',
    'description': 'Override datastore client',
    'long_description': "# Arcane Datastore\n\nThis package is based on [google-cloud-datastore](https://pypi.org/project/google-cloud-datastore/).\n\n## Get Started\n\n```sh\npip install arcane-datastore\n```\n\n## Example Usage\n\n```python\nfrom arcane import datastore\nclient = datastore.Client()\n\nentity = client.get_entity('kind-id-here', 1)\n```\n\nor\n\n```python\nfrom arcane import datastore\n\n# Import your configs\nfrom configure import Config\n\nclient = datastore.Client.from_service_account_json(Config.KEY, project=Config.GCP_PROJECT)\n\nentity = client.get_entity('kind-id-here', 1)\n```\n",
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
