# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cord',
 'encord',
 'encord.constants',
 'encord.http',
 'encord.objects',
 'encord.orm',
 'encord.project_ontology',
 'encord.utilities']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=3.4.8,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests==2.25.0',
 'tqdm>=4.32.1,<5.0.0',
 'uuid>=1.30,<2.0']

setup_kwargs = {
    'name': 'encord',
    'version': '0.1.42',
    'description': 'Encord Python SDK Client',
    'long_description': '<h1 align="center">\n  <p align="center">Encord Python API Client</p>\n  <a href="https://encord.com"><img src="https://encord.com/logo512.png" width="150" alt="Cord logo"/></a>\n</h1>\n\n[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n\n***The data engine for computer vision***\n\n## 💻 Features\n\n- Minimal low-level Python client that allows you to interact with Encord\'s API\n- Supports Python: `3.7`, `3.8`, `3.9`, and `3.10`\n\n## ✨ Relevant Links\n* [Encord website](https://encord.com)\n* [Encord web app](https://app.encord.com)\n* [Encord documentation](https://docs.encord.com)\n\n## 💡 Getting Started\n\nFor full documentation, please visit [Encord Python SDK](https://python.docs.encord.com/).\n\nFirst, install Encord Python API Client using the [pip](https://pip.pypa.io/en/stable/installing) package manager:\n\n```bash\npip install encord\n```\n\nThen, create an API key for authentication via the [Encord web app](https://app.encord.com). Pass the resource ID and API key as environment variables or pass them explicitly when you initialise the EncordClient object.\n\n```bash\nexport ENCORD_PROJECT_ID="<project_id>"\nexport ENCORD_API_KEY="<project_api_key>"\n```\n\nPassing the resource ID and API key as environment variables, you can initialise the Encord client directly.\n\n```python\nfrom encord.client import EncordClient\n\nclient = EncordClient.initialise()\n```\n\nIf you want to avoid setting environment variables, you can initialise the Encord client by passing the resource ID and API key as strings.\n\n```python\nfrom encord.client import EncordClient\n\nclient = EncordClient.initialise("<resource_id>", "<resource_api_key>")\n```\n\nIf you wish to instantiate several client objects and avoid passing parameters each time, you can instantiate a EncordConfig object, pass the resource ID and API key as strings, and initialise the client with the config object.\n\n```py\nfrom encord.client import EncordClient\nfrom encord.client import EncordConfig\n\nconfig = EncordConfig("<resource_id>", "<resource_api_key>")\nclient = EncordClient.initialise_with_config(config)\n```\n\nOnce you have instantiated an Encord client, it is easy to fetch information associated with the given resource ID.\n\n```py\nfrom encord.client import EncordClient\n\nclient = EncordClient.initialise()\nproject = client.get_project()\n```\n\n## 🐛 Troubleshooting\n\nPlease report bugs to [GitHub Issues](https://github.com/encord-team/encord-client-python/issues). Just make sure you read the [Encord documentation](https://docs.encord.com) and search for related issues first.\n',
    'author': 'Cord Technologies Limited',
    'author_email': 'hello@encord.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/encord-team/encord-client-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
