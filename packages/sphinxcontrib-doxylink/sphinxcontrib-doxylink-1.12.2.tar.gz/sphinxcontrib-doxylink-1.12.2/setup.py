# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinxcontrib', 'sphinxcontrib.doxylink']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx>=1.6', 'pyparsing>=3.0.8,<4.0.0', 'python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'sphinxcontrib-doxylink',
    'version': '1.12.2',
    'description': 'Sphinx extension for linking to Doxygen documentation.',
    'long_description': '######################\nsphinxcontrib-doxylink\n######################\n\nA Sphinx_ extension to link to external Doxygen API documentation.\n\nUsage\n-----\n\nPlease refer to the documentation_ for information on using this extension.\n\nInstallation\n------------\n\nThis extension can be installed from the Python Package Index::\n\n   pip install sphinxcontrib-doxylink\n\n.. _`Sphinx`: http://www.sphinx-doc.org\n.. _`documentation`: http://sphinxcontrib-doxylink.readthedocs.io/en/stable/\n',
    'author': 'Matt Williams',
    'author_email': 'matt@milliams.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sphinx-contrib/doxylink',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
