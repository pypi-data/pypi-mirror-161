# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nbpretty']

package_data = \
{'': ['*'], 'nbpretty': ['templates/nbpretty/*', 'templates/nbpretty/static/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0,<9.0',
 'ipython>=8.0.0,<9.0.0',
 'jinja2<3.1',
 'livereload>=2.0.0,<3.0.0',
 'nbconvert>=6.4.0,<7.0.0',
 'rich>=12.0.0,<13.0.0']

entry_points = \
{'console_scripts': ['nbpretty = nbpretty:main']}

setup_kwargs = {
    'name': 'nbpretty',
    'version': '0.2.14',
    'description': 'A tool to convert sets of Jupyter notebook files into a single, cohesive set of linked pages',
    'long_description': 'nbpretty\n========\n\nnbpretty is a tool to convert sets of notebook files into a single, cohesive set of linked pages.\n\nDocumentation at https://nbpretty.readthedocs.io\n',
    'author': 'Matt Williams',
    'author_email': 'matt@milliams.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/milliams/nbpretty',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
