# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['huemon',
 'huemon.api',
 'huemon.commands',
 'huemon.commands.internal',
 'huemon.discoveries',
 'huemon.discoveries.internal',
 'huemon.infrastructure',
 'huemon.utils',
 'huemon.utils.monads']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'fastapi>=0.75.0,<0.76.0',
 'types-PyYAML>=6.0.4,<7.0.0',
 'uvicorn>=0.17.5,<0.18.0']

setup_kwargs = {
    'name': 'huemon',
    'version': '0.9.2',
    'description': 'Monitor your Philips Hue network',
    'long_description': '# Huemon\n\n[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)\n[![Build](https://github.com/edeckers/huemon/actions/workflows/test.yml/badge.svg?branch=develop)](https://github.com/edeckers/huemon/actions/workflows/test.yml)\n[![PyPI](https://img.shields.io/pypi/v/huemon.svg?maxAge=3600)](https://pypi.org/project/huemon)\n[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)\n\nZabbix monitoring with low-level discovery for Philips Hue networks.\n\n![Dashboard: sensors](https://raw.githubusercontent.com/edeckers/huemon/develop/assets/docs/dashboard-sensors.png?raw=true "Dashboard: sensors")\n\n## Requirements\n\n- Zabbix server 5.0+\n- Zabbix agent 5.0+\n- Python 3.7+ on Zabbix agent machine\n\n## Installation\n\n```bash\npip3 install huemon\n```\n\n## Configuration\n\n1. Copy `config.example.yml` from `src/huemon` to `/path/to/config.yml`\n2. Make necessary changes\n3. Provide the path through environment variable `HUEMON_CONFIG_PATH`\n\n### Plugins\n\nCreate a command or discovery plugin by implementing [HueCommand](src/huemon/commands/hue_command_interface.py) or [Discovery](src/huemon/discoveries/discovery_interface.py) respectively and copy the file to the configured path in `plugins.commands.path` or `plugins.discoveries.path` of the configuration file.\n\n### Zabbix agent configuration\n\n```\n# file:/path/to/zabbix/agent/conf.d/hue.conf\n\nUserParameter=hue.discovery[*],HUEMON_CONFIG_PATH=/path/to/config.yml /usr/bin/python3 -m huemon discover $1\nUserParameter=hue.value[*],HUEMON_CONFIG_PATH=/path/to/config.yml /usr/bin/python3 -m huemon $1 $2 $3\n```\n\nOr Docker\n\n```\n# file:/path/to/zabbix/agent/conf.d/hue.conf\n\nUserParameter=hue.discovery[*],docker-compose run huemon discover $1\nUserParameter=hue.value[*],docker-compose run huemon $1 $2 $3\n```\n\nOr _agent mode_\n\n```\n# file:/path/to/zabbix/agent/conf.d/hue.conf\n\nUserParameter=hue.discovery[*],curl http://127.0.0.1:8000/discover?q=$1\nUserParameter=hue.value[*],curl http://127.0.0.1:8000/$1?q=$2\\&q=$3\n```\n\n### Configure Systemd service\n\nAn installer that configures Huemon as a Systemd service is included in this repository. It uses `/etc/huemon/config.yml` as the configuration path.\n\n```bash\nassets/service-installer.sh install\n```\n\n## Usage\n\n### Shell\n\n```bash\nHUEMON_CONFIG_PATH=/usr/bin/python3 -m huemon discover lights\n```\n\nOr _agent mode_\n\n```bash\nHUEMON_CONFIG_PATH=/usr/bin/python3 -m huemon agent start\n```\n\n### Docker\n\nProvide a configuration path for the `huemon-config` volume in `docker-compose.yml` before running the commands below.\n\n```bash\ndocker-compose run huemon discover lights\n```\n\nOr _agent mode_\n\n```bash\ndocker-compose up -d\n```\n\n## Screenshots\n\n### Dashboards\n![Dashboard: sensors](https://raw.githubusercontent.com/edeckers/huemon/develop/assets/docs/dashboard-sensors.png?raw=true "Dashboard: sensors")\n\n### Discoveries\n\n![Discoveries: batteries](https://raw.githubusercontent.com/edeckers/huemon/develop/assets/docs/discoveries-batteries.png?raw=true "Discoveries: batteries")\n\n![Discoveries: lights](https://raw.githubusercontent.com/edeckers/huemon/develop/assets/docs/discoveries-lights.png?raw=true "Discoveries: lights")\n\n![Discoveries: sensors](https://raw.githubusercontent.com/edeckers/huemon/develop/assets/docs/discoveries-sensors.png?raw=true "Discoveries: sensors")\n\n### Template\n\n![Template](https://raw.githubusercontent.com/edeckers/huemon/develop/assets/docs/template-discoveries.png?raw=true "Template")\n\n## Contributing\n\nSee the [contributing guide](CONTRIBUTING.md) to learn how to contribute to the  repository and the development workflow.\n\n## Code of Conduct\n\n[Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.\n\n## License\n\nMPL-2.0\n',
    'author': 'Ely Deckers',
    'author_email': None,
    'maintainer': 'Ely Deckers',
    'maintainer_email': None,
    'url': 'https://github.com/edeckers/huemon.git',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
