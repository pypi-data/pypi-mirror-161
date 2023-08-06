# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strict_fields', 'strict_fields.tests']

package_data = \
{'': ['*']}

install_requires = \
['django>=2']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

setup_kwargs = {
    'name': 'django-strict-fields',
    'version': '1.0.2',
    'description': 'A collection of fields and utilities to help make model fields more strict.',
    'long_description': 'django-strict-fields\n########################################################################\n\nThis library is meant to help enforce stricter rules around using some of the basic model fields that Django provides.\nView the docs `here <https://django-strict-fields.readthedocs.io/>`_ to get started.\n\nDocumentation\n=============\n\n`View the django-strict-fields docs here\n<https://django-strict-fields.readthedocs.io/>`_.\n\nInstallation\n============\n\nInstall django-strict-fields with::\n\n    pip3 install django-strict-fields\n\nAfter this, add ``strict_fields`` to the ``INSTALLED_APPS``\nsetting of your Django project.\n\nContributing Guide\n==================\n\nFor information on setting up django-strict-fields for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\nPrimary Authors\n===============\n\n*   @tomage: Tómas Árni Jónasson\n',
    'author': 'Tomas Arni Jonasson',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/django-strict-fields',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
