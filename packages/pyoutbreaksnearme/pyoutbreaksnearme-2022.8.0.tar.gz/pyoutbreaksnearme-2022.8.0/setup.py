# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyoutbreaksnearme', 'pyoutbreaksnearme.data', 'pyoutbreaksnearme.util']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.0', 'ujson>=5.4.0,<6.0.0']

setup_kwargs = {
    'name': 'pyoutbreaksnearme',
    'version': '2022.8.0',
    'description': 'A Python3 API for Outbreaks Near Me',
    'long_description': '# 🚰 pyoutbreaksnearme: A Python3 API for Outbreaks Near Me\n\n[![CI](https://github.com/bachya/pyoutbreaksnearme/workflows/CI/badge.svg)](https://github.com/bachya/pyoutbreaksnearme/actions)\n[![PyPi](https://img.shields.io/pypi/v/pyoutbreaksnearme.svg)](https://pypi.python.org/pypi/pyoutbreaksnearme)\n[![Version](https://img.shields.io/pypi/pyversions/pyoutbreaksnearme.svg)](https://pypi.python.org/pypi/pyoutbreaksnearme)\n[![License](https://img.shields.io/pypi/l/pyoutbreaksnearme.svg)](https://github.com/bachya/pyoutbreaksnearme/blob/master/LICENSE)\n[![Code Coverage](https://codecov.io/gh/bachya/pyoutbreaksnearme/branch/master/graph/badge.svg)](https://codecov.io/gh/bachya/pyoutbreaksnearme)\n[![Maintainability](https://api.codeclimate.com/v1/badges/4707fac476249d515511/maintainability)](https://codeclimate.com/github/bachya/pyoutbreaksnearme/maintainability)\n[![Say Thanks](https://img.shields.io/badge/SayThanks-!-1EAEDB.svg)](https://saythanks.io/to/bachya)\n\n<a href="https://www.buymeacoffee.com/bachya1208P" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>\n\n`pyoutbreaksnearme` is a Python3, asyncio-based library for getting data from\n[Outbreaks Near Me](https://outbreaksnearme.org).\n\n- [Installation](#installation)\n- [Python Versions](#python-versions)\n- [Usage](#usage)\n- [Contributing](#contributing)\n\n# Installation\n\n```python\npip install pyoutbreaksnearme\n```\n\n# Python Versions\n\n`pyoutbreaksnearme` is currently supported on:\n\n* Python 3.8\n* Python 3.9\n* Python 3.10\n\n# Usage\n\n```python\nimport asyncio\n\nfrom aiohttp import ClientSession\n\nfrom pyoutbreaksnearme import Client\n\n\nasync def main() -> None:\n    """Create the aiohttp session and run the example."""\n    client = await Client()\n\n    # Get user-reported data for the location closest to a latitude/longitude:\n    nearest_user_data = await client.user_data.async_get_nearest_by_coordinates(\n        40.7152, -73.9877\n    )\n\n    # Get totals for user-reported data:\n    user_totals_data = await client.user_data.async_get_totals()\n\n    # Get CDC data for the location closest to a latitude/longitude:\n    nearest_user_data = await client.cdc_data.async_get_nearest_by_coordinates(\n        40.7152, -73.9877\n    )\n\n\nasyncio.run(main())\n```\n\nBy default, the library creates a new connection to Outbreaks Near Me with each\ncoroutine. If you are calling a large number of coroutines (or merely want to squeeze\nout every second of runtime savings possible), an\n[`aiohttp`](https://github.com/aio-libs/aiohttp) `ClientSession` can be used for connection\npooling:\n\n```python\nimport asyncio\n\nfrom aiohttp import ClientSession\n\nfrom pyoutbreaksnearme import Client\n\n\nasync def main() -> None:\n    """Create the aiohttp session and run the example."""\n    async with ClientSession() as session:\n        # Create a Notion API client:\n        client = await Client(session=session)\n\n        # Get to work...\n\n\nasyncio.run(main())\n```\n\n# Contributing\n\n1. [Check for open features/bugs](https://github.com/bachya/pyoutbreaksnearme/issues)\n  or [initiate a discussion on one](https://github.com/bachya/pyoutbreaksnearme/issues/new).\n2. [Fork the repository](https://github.com/bachya/pyoutbreaksnearme/fork).\n3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`\n4. (_optional, but highly recommended_) Enter the virtual environment: `source ./.venv/bin/activate`\n5. Install the dev environment: `script/setup`\n6. Code your new feature or bug fix.\n7. Write tests that cover your new functionality.\n8. Run tests and ensure 100% code coverage: `nox -rs coverage`\n9. Update `README.md` with any new documentation.\n10. Add yourself to `AUTHORS.md`.\n11. Submit a pull request!\n',
    'author': 'Aaron Bach',
    'author_email': 'bachya1208@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bachya/pyoutbreaksnearme',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
