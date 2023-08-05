# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ansible_generator']

package_data = \
{'': ['*']}

install_requires = \
['ansible', 'sentry-sdk>=1.9.0,<2.0.0']

entry_points = \
{'console_scripts': ['ansible-generate = ansible_generator:cli']}

setup_kwargs = {
    'name': 'ansible-generator',
    'version': '3.1.1',
    'description': 'Ansible project generation tool',
    'long_description': "# Ansible Generator\n\n## Description\n\nAnsible Generator is a python program designed to simplify creating a new\nansible playbook by creating the necessary directory structure for the user\nbased on ansible's best practices, as outlined in [content organization best practices](https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#content-organization).\n\n## Installation\n\n### PIP (recommended)\n\n```\npip install -U ansible-generator\n```\n\n### Source\n\n```\ngit clone https://github.com/kkirsche/ansible-generator.git\ncd ansible-generator\ncurl -sSL https://install.python-poetry.org | python3 -\npoetry build\n```\n\n## Usage\n\n### Help Text\n\n```\nusage: ansible-generate [-h] [-a] [-i INVENTORIES [INVENTORIES ...]]\n                        [-r ROLES [ROLES ...]] [-v]\n                        [-p PROJECTS [PROJECTS ...]] [--version]\n\nGenerate an ansible playbook directory structure\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -a, --alternate-layout\n  -i INVENTORIES [INVENTORIES ...], --inventories INVENTORIES [INVENTORIES ...]\n  -r ROLES [ROLES ...], --roles ROLES [ROLES ...]\n  -v, --verbose\n  -p PROJECTS [PROJECTS ...], --projects PROJECTS [PROJECTS ...]\n  --version             show program's version number and exit\n```\n\n#### Defaults\n\n- `alternate-layout` --- `False`\n- `verbose` --- `False`\n- `inventories` --- `['production', 'staging']`\n- `roles` --- `[]`\n- `projects` --- `[]`\n\n### Example\n\n#### Current directory\n\n```\nansible-generate\n```\n\n#### New-project\n\n```\nansible-generate -p playbook_name\n```\n\n#### Alternate Layout\n\n```\nansible-generate -a\n```\n\n#### Custom Inventories\n\n```\nansible-generate -i production staging lab\n```\n\n#### Roles\n\nThis portion of the tool relies on Ansible's `ansible-galaxy` command line\napplication\n\n```\nansible-generate -r role1 role2\n```\n\n#### Output\n\n```\n~/Downloads ❯❯❯ ansible-generate -i production staging lab -r common ubuntu centos -a -p network_security_baseline\ncreating directory /Users/example_user/Downloads/network_security_baseline/roles\ncreating directory /Users/example_user/Downloads/network_security_baseline/inventories/production/group_vars\ncreating directory /Users/example_user/Downloads/network_security_baseline/inventories/production/host_vars\ncreating directory /Users/example_user/Downloads/network_security_baseline/inventories/staging/group_vars\ncreating directory /Users/example_user/Downloads/network_security_baseline/inventories/staging/host_vars\ncreating directory /Users/example_user/Downloads/network_security_baseline/inventories/lab/group_vars\ncreating directory /Users/example_user/Downloads/network_security_baseline/inventories/lab/host_vars\ncreating file /Users/example_user/Downloads/network_security_baseline/inventories/production/hosts\ncreating file /Users/example_user/Downloads/network_security_baseline/inventories/staging/hosts\ncreating file /Users/example_user/Downloads/network_security_baseline/inventories/lab/hosts\ncreating file /Users/example_user/Downloads/network_security_baseline/site.yml\nansible galaxy output for role common:\n- common was created successfully\nansible galaxy output for role ubuntu:\n- ubuntu was created successfully\nansible galaxy output for role centos:\n- centos was created successfully\n```\n",
    'author': 'Kevin Kirsche',
    'author_email': 'kev.kirsche@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kkirsche/ansible-generator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
