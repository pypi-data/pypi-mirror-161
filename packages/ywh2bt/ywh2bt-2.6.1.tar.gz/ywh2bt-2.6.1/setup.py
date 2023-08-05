# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ywh2bt',
 'ywh2bt.cli',
 'ywh2bt.cli.commands',
 'ywh2bt.core',
 'ywh2bt.core.api',
 'ywh2bt.core.api.formatter',
 'ywh2bt.core.api.models',
 'ywh2bt.core.api.trackers',
 'ywh2bt.core.api.trackers.github',
 'ywh2bt.core.api.trackers.jira',
 'ywh2bt.core.api.trackers.servicenow',
 'ywh2bt.core.configuration',
 'ywh2bt.core.configuration.trackers',
 'ywh2bt.core.converter',
 'ywh2bt.core.crypt',
 'ywh2bt.core.factories',
 'ywh2bt.core.schema',
 'ywh2bt.core.serializers',
 'ywh2bt.core.state',
 'ywh2bt.core.synchronizer',
 'ywh2bt.core.tester',
 'ywh2bt.gui',
 'ywh2bt.gui.dialog',
 'ywh2bt.gui.widgets',
 'ywh2bt.gui.widgets.attribute',
 'ywh2bt.gui.widgets.thread']

package_data = \
{'': ['*'],
 'ywh2bt.gui': ['resources/icons/*',
                'resources/icons/types/*',
                'resources/icons/types/TrackerConfiguration/*',
                'resources/translations/*']}

install_requires = \
['PyGithub>=1.53,<2.0',
 'PySide2>=5.15.1,<6.0.0',
 'aiosnow>=0.6.0,<0.7.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'html2text>=2020.1.16,<2021.0.0',
 'jira>=3.1.0,<4.0.0',
 'lxml>=4.5.2,<5.0.0',
 'markdown>=3.3.3,<4.0.0',
 'python-gitlab>=2.5.0,<3.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.24.0,<3.0.0',
 'ruamel.yaml>=0.16.12,<0.17.0',
 'singledispatchmethod>=1.0,<2.0',
 'tomlkit>=0.7.0,<0.8.0',
 'types-Markdown',
 'types-chardet',
 'types-requests',
 'types-setuptools',
 'typing-extensions',
 'yeswehack>=0.7.2,<1']

entry_points = \
{'console_scripts': ['ywh2bt = ywh2bt.cli.main:run',
                     'ywh2bt-gui = ywh2bt.gui.main:run']}

setup_kwargs = {
    'name': 'ywh2bt',
    'version': '2.6.1',
    'description': 'ywh2bt - YesWeHack to Bug Tracker',
    'long_description': '# ywh2bt\n\nywh2bt synchronizes your vulnerability reports from the [Yes We Hack platform][YesWeHack-Platform]\nwith issues of your bug tracker(s). It automatically retrieves reports you want to copy in your bug tracker,\ncreates the related issue, and syncs further updates between issues and reports.  \nIt comes with a handy GUI to set up and test the integration,\nwhile completely controlling the information you allow to be synchronized from both side.\n\n![Screenshot of GUI with loaded example file](docs/img/screenshot-gui-example.png)\n\n## Table of contents\n\n- [User Guide](#user-guide)\n- [Architecture](#architecture)\n- [Requirements](#requirements)\n- [Installation](#installation)\n- [Supported trackers](#supported-trackers)\n- [Changelog](#changelog)\n- [Local development](#local-development)\n    - [Requirements](#requirements-1)\n    - [Installation](#installation-1)\n    - [Usage](#usage-1)\n    - [Updating User Guide](#updating-user-guide)\n\n## User Guide\n\nA User Guide is available in [PDF][User-Guide-pdf] and [HTML][User-Guide-html] formats.\n\n## Architecture\n\nYWH2BT embeds both the GUI to set up the integration,\nand the application to be scheduled on your server to periodically poll and synchronize new reports.  \nYou can either run both on a single machine, or prepare the configuration file\non a computer (with the GUI) and transfer it on the server and use it through a scheduled command.\n\nSince data is pulled from YWH platform to your server, only regular outbound web connections need to be authorized on your server.\n\n## Requirements\n\n- `python` >= 3.7,<=3.9\n- [`pip`](https://pip.pypa.io/en/stable/installing/)\n\n## Supported trackers\n\n- github\n- gitlab\n- jira / jiracloud\n- servicenow\n\n## Changelog\n\n- v2.5:\n    - added Personal Access Token (PAT) authentication\n    - removed OAuth authentication\n- v2.4:\n    - added option to prevent recreation of issues that were created by a previous synchronization\n      but are not found into the bug tracker anymore\n- v2.3:\n    - added support for ServiceNow\n- v2.2:\n    - added GitLab option for confidential issues\n- v2.1:\n    - added feedback feature (synchronize from bug tracker to report)\n    - added [docker image yeswehack/ywh2bugtracker](https://hub.docker.com/r/yeswehack/ywh2bugtracker)\n    - added User Guide [PDF][User-Guide-pdf] and [HTML][User-Guide-html]\n- v0.* to v2.0.0:\n    - behavior changes:\n        - reports logs can selectively be synchronized with the trackers:\n            - public comments\n            - private comments\n            - report details changes\n            - report status changes\n            - rewards\n        - a program can now only be synchronized with 1 tracker\n    - added support for JSON configuration files\n    - removed `ywh-bugtracker` command (use `ywh2bt synchronize`)\n    - added `ywh2bt` command:\n        - added `ywh2bt synchronize`:\n            - note: `ywh2bt synchronize --config-file FILE --config-format FORMAT` \n              is the equivalent of `ywh-bugtracker -n -f FILE` in v0.*\n        - added `ywh2bt validate`\n        - added `ywh2bt test`\n        - added `ywh2bt convert`\n        - added `ywh2bt schema`\n    - removed command line interactive mode\n    - added GUI via `ywh2bt-gui` command\n\n## Local development\n\n### Requirements\n\n- [`poetry`](https://python-poetry.org/) (`pip install poetry`)\n\n### Installation\n\n- `make install` (or `poetry install`): creates a virtualenv and install dependencies\n\n### Usage\n\nInstead of `ywh2bt [command]`, run commands using `poetry run ywh2bt [command]`.\n\nSame goes for `ywh2bt-gui`, run `poetry run ywh2bt-gui` instead.\n\n### Updating User Guide\n\n[PDF][User-Guide-pdf] and [HTML][User-Guide-html] versions of the User Guide are generated via Pandoc\nusing [docs/User-Guide.md][User-Guide-md] as an input file.  \nAny changes made to [docs/User-Guide.md][User-Guide-md] **must be followed** by the execution of the command\n`make user-guide` in order to regenerate the PDF and HTML files, **otherwise the CI will fail**.\n\n[YesWeHack-Platform]: https://www.yeswehack.com/\n\n[User-Guide-md]: docs/User-Guide.md\n\n[User-Guide-pdf]: docs/user-guide/User-Guide.pdf\n\n[User-Guide-html]: docs/user-guide/User-Guide.html\n',
    'author': 'm.honel',
    'author_email': 'm.honel@yeswehack.com',
    'maintainer': 'YesWeHack',
    'maintainer_email': 'project@yeswehack.com',
    'url': 'https://github.com/yeswehack/ywh2bugtracker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<3.10',
}


setup(**setup_kwargs)
