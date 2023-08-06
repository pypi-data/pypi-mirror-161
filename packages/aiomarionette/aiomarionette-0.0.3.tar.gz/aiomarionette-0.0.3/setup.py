# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aiomarionette']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aiomarionette',
    'version': '0.0.3',
    'description': 'Firefox Marionette client for asyncio',
    'long_description': "# FireFox Marionette Client for *asyncio*\n\n*aiomarionette* provides an asynchronous client interface for the [Firefox\nMarionette] remote control protocol.\n\n[Firefox Marionette]: https://firefox-source-docs.mozilla.org/testing/marionette/index.html\n\n## Usage\n\nTo use *aiomarionette*, create an instance of the `Marionette` class.  By\ndefault, the cclient will attempt to connect to the Marionette socket on the\nlocal machine, port 2828.  You can specify the `host` and/or `port` arguments to\nchange this.  Be sure to call the `connect` method first, before calling any\nof the command methods.\n\n```python\nasync with aiomarionette.Marionette() as mn:\n    mn.connect()\n    mn.navigate('https://getfirefox.com/')\n```\n\n## Compared to *marionette_driver*\n\nThe official Python client for Firefox Marionette is [marionette_driver].\nAlthough it is more complete than *aiomarionette* (at least for now), it only\nprovides a blocking API.\n\nUnlike *marionette_driver*, *aiomarionette* does not currently support launching\nFirefox directly.  You must explicity start a Firefox process in Marionette mode\nbefore connecting to it with *aiomarionette*.\n\n[marionette_driver]: https://pypi.org/project/marionette-driver/\n",
    'author': 'Dustin C. Hatch',
    'author_email': 'dustin@hatch.name',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AdmiralNemo/aiomarionette',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
