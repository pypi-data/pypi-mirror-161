# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitlabtree']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'rich>=12.5.1,<13.0.0',
 'typer>=0.6.1,<0.7.0',
 'types-requests>=2.28.5,<3.0.0']

entry_points = \
{'console_scripts': ['gitlabtree = gitlabtree.main:app']}

setup_kwargs = {
    'name': 'gitlabtree',
    'version': '0.1.0',
    'description': 'CLI tool for gathering GitLab information in tree format',
    'long_description': '# GitLab🌲\n\nGitLabTree is a CLI tool for retrieving information from a GitLab server. Mainly in a tree format, as the name suggests.\n\n\n## Install\n\n```\npip install ...\n```\n\nFrom source:\n```\ngit clone\ncd gitlabtree\npoetry install\n```\n',
    'author': 'ubaumann',
    'author_email': 'github@m.ubaumann.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
