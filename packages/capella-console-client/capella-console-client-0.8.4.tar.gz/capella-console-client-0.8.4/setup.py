# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['capella_console_client',
 'capella_console_client.cli',
 'capella_console_client.cli.user_searches']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.18.2,<0.19.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'retrying>=1.3.3,<2.0.0',
 'rich>=10.16.2,<11.0.0']

extras_require = \
{'docs': ['Sphinx>=4.3.2,<5.0.0',
          'sphinx-rtd-theme>=1.0.0,<2.0.0',
          'sphinx-autobuild>=2021.3.14,<2022.0.0',
          'sphinx-copybutton>=0.4.0,<0.5.0',
          'sphinx-autodoc-typehints>=1.11.1,<2.0.0'],
 'wizard': ['typer>=0.4.0,<0.5.0',
            'questionary>=1.10.0,<2.0.0',
            'tabulate>=0.8.9,<0.9.0']}

entry_points = \
{'console_scripts': ['capella-console-wizard = '
                     'capella_console_client.cli.wizard:main']}

setup_kwargs = {
    'name': 'capella-console-client',
    'version': '0.8.4',
    'description': 'Python SDK for api.capellaspace.com (search, order, download)',
    'long_description': '# 🛰️ capella-console-client 🐐\n\n[![Version](https://img.shields.io/pypi/v/capella-console-client.svg)](https://pypi.org/project/capella-console-client/)\n[![License](https://img.shields.io/pypi/l/capella-console-client.svg)](#)\n[![CI](https://github.com/capellaspace/console-client/workflows/CI/badge.svg)](#)\n[![Coverage](https://coveralls.io/repos/github/capellaspace/console-client/badge.svg?branch=main)](https://coveralls.io/github/capellaspace/console-client)\n[![Supported Python Versions](https://img.shields.io/pypi/pyversions/capella-console-client.svg)](https://pypi.org/project/capella-console-client/)\n[![Documentation](https://readthedocs.org/projects/capella-console-client/badge/?version=main)](https://capella-console-client.readthedocs.io)\n\nPython SDK for api.capellaspace.com (search, order, download)\n\n\n## Installation\n\n```bash\npip install capella-console-client\n```\n\n## Requirements\n\n* python >= 3.6\n* `capella-console-client` requires an active account on [console.capellaspace.com](https://console.capellaspace.com/). Sign up for an account at [https://www.capellaspace.com/community/](https://www.capellaspace.com/community/).\n\n\n## Usage\n\n![Quickstart](docs/images/quickstart.gif)\n\n```python\nfrom capella_console_client import CapellaConsoleClient\n\n# you will be prompted for console user (user@email.com)/ password before authenticating\nclient = CapellaConsoleClient(\n    verbose=True\n)\n\n# search for 2 open-data products\nstac_items = client.search(\n    instrument_mode="spotlight",\n    product_type__in=["SLC", "GEO"],\n    collections=["capella-open-data"],\n    limit=2\n)\n\n# order\norder_id = client.submit_order(items=stac_items, omit_search=True)\n\n# download\nproduct_paths = client.download_products(\n    order_id=order_id, \n    local_dir=\'/tmp\',\n    show_progress=True\n)\n```\n\n\n## Documentation\n\nThe documentation for `capella-console-client` can be found [here](https://capella-console-client.readthedocs.io).\n\n## 🧙\u200d capella-console-wizard 🧙\u200d♂️\nstarting with `capella-console-client>=0.8.0` the SDK ships with an interactive wizard-like CLI: `capella-console-wizard` \n\n### Installation\n```\npip install capella-console-client[wizard]\n```\n\n### Usage\n```\ncapella-console-wizard --help\n```\n\nsee \n\n\n## Support\n\nPlease [open an issue](https://github.com/capellaspace/console-client/issues/new)\nwith enough information for us to reproduce your problem.\nA [minimal, reproducible example](https://stackoverflow.com/help/minimal-reproducible-example)\nwould be very helpful.\n\n## Contributing\n\nContributions are very much welcomed and appreciated. See [how to contribute](https://capella-console-client.readthedocs.io/en/main/pages/contributors.html) for more information.\n\n\n## License\n• Licensed under the [MIT License](https://github.com/capellaspace/console-client/blob/master/LICENSE) • Copyright 2021 • Capella Space •\n',
    'author': 'Thomas Beyer',
    'author_email': 'thomas.beyer@capellaspace.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/capellaspace/console-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
