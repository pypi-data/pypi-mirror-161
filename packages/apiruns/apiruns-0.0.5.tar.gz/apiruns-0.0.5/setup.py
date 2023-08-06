# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apiruns']

package_data = \
{'': ['*']}

install_requires = \
['Cerberus>=1.3.4,<2.0.0',
 'PyYAML>=6.0,<7.0',
 'httpx>=0.23.0,<0.24.0',
 'requests>=2.28.1,<3.0.0',
 'typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['apiruns = apiruns.main:app']}

setup_kwargs = {
    'name': 'apiruns',
    'version': '0.0.5',
    'description': 'Apiruns CLI is a tool to make self-configurable rest API.',
    'long_description': '# apiruns-cli\n\nApiruns CLI is a tool to make self-configurable rest API. Create an API rest has never been so easy.\n\n## Requirements\n\n- Python 3.6+\n\n## Installation.\n\n```bash\npip install apiruns\n```\n\n```bash\npoetry install\n```\n\n## Example\n\n```bash\napiruns --help\n\n Usage: apiruns [OPTIONS] COMMAND [ARGS]...\n \n╭─ Options───────────────────────────────────────────────────────────────────╮\n│ --help          Show this message and exit.                                │\n╰────────────────────────────────────────────────────────────────────────────╯\n╭─ Commands ─────────────────────────────────────────────────────────────────╮\n│ build                       Build images & validate schema.🔧              │\n│ down                        Stops containers and removes containers. 🌪    │\n│ up                          Make your API rest. 🚀                         │\n│ version                     Get current version. 💬                        │\n╰────────────────────────────────────────────────────────────────────────────╯\n```\n\n## file configuration\n\nMake YAML file to configure your application’s services. `api.yml`\n\n```yml\n# This is an example manifest to create microservices in apiruns.\n\nmyapi: # Microservices name.\n\n  # first endpoint\n  - path: /users/ # Path name.\n    schema: # Schema of data structure.\n      username:\n        type: string\n        required: true\n      age:\n        type: integer\n        required: true\n      is_admin:\n        type: boolean\n        required: true\n      level:\n        type: string\n```\n\n## Crear a API Rest\n\n```bash\napiruns up --file examples/api.yml \n\nBuilding API\nCreating DB container.\nCreating API container.\nStarting services\nAPI listen on 8000\n```\n',
    'author': 'Jose Salas',
    'author_email': 'jose.salas@apiruns.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/apiruns/apiruns-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
