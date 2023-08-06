# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_table_sort']

package_data = \
{'': ['*'], 'django_table_sort': ['static/*']}

install_requires = \
['django>=3.0']

setup_kwargs = {
    'name': 'django-table-sort',
    'version': '0.1.0a0',
    'description': '',
    'long_description': '# Django-table-sort\n\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/TheRealVizard/django-table-sort/main.svg)](https://results.pre-commit.ci/latest/github/TheRealVizard/django-table-sort/main) ![django-table-sort](https://badge.fury.io/py/django-table-sort.svg)\n![downloads](https://img.shields.io/pypi/dm/django-table-sort)\n\nCreate tables with sorting on the headers in Django templates.\n',
    'author': 'TheRealVizard',
    'author_email': 'vizard@divineslns.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
