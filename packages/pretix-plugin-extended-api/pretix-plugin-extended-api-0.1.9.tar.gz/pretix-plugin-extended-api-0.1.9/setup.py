# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pretix_extended_api', 'pretix_extended_api.views']

package_data = \
{'': ['*'],
 'pretix_extended_api': ['locale/de/LC_MESSAGES/*',
                         'locale/de_Informal/*',
                         'locale/de_Informal/LC_MESSAGES/*',
                         'static/pretix_extended_api/*',
                         'templates/pretix_extended_api/*']}

entry_points = \
{'pretix.plugin': ['pretix_extended_api = '
                   'pretix_extended_api:PretixPluginMeta']}

setup_kwargs = {
    'name': 'pretix-plugin-extended-api',
    'version': '0.1.9',
    'description': 'Extend the REST API to expose more information needed by the PyCon Italia repository.',
    'long_description': None,
    'author': 'Python Italia',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
