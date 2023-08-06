# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['render_engine', 'render_engine.parsers', 'render_engine.templates']

package_data = \
{'': ['*'], 'render_engine.templates': ['xml/*']}

install_requires = \
['Jinja2>=3.1.0,<4.0.0',
 'markdown2>=2.4.2,<3.0.0',
 'more-itertools>=8.12.0,<9.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'python-frontmatter>=1.0.0,<2.0.0',
 'python-slugify>=6.1.1,<7.0.0',
 'rich>=12.4.0,<13.0.0']

setup_kwargs = {
    'name': 'render-engine',
    'version': '2022.7.2',
    'description': 'Static Site Generator with a Flask-like flair',
    'long_description': None,
    'author': 'Jay Miller',
    'author_email': 'kjaymiller@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.7,<4.0.0',
}


setup(**setup_kwargs)
