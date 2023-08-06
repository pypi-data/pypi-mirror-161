# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitlabtree']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1,<2',
 'requests>=2,<3',
 'rich>=12,<13',
 'typer>=0.6,<0.7',
 'types-requests>=2,<3']

entry_points = \
{'console_scripts': ['gitlabtree = gitlabtree.main:app']}

setup_kwargs = {
    'name': 'gitlabtree',
    'version': '0.1.1',
    'description': 'CLI tool for gathering GitLab information in tree format',
    'long_description': '# GitLab🌲\n\nGitLabTree is a CLI tool for retrieving information from a GitLab server. Mainly in a tree format, as the name suggests.\n\n\n## Install\n\n```\npip install gitlabtree\n```\n\nFrom source:\n```\ngit clone\ncd gitlabtree\npoetry install\n```\n\n## Features\n\n### Help\n\n![help](https://github.com/INSRapperswil/gitlabtree/blob/main/doc/imgs/gitlabtree_help.png)\n\n### Permissions\n\n![help](https://github.com/INSRapperswil/gitlabtree/blob/main/doc/imgs/gitlabtree_permissions.png)\n\n### Pipeline\n\n![help](https://github.com/INSRapperswil/gitlabtree/blob/main/doc/imgs/gitlabtree_pipeline.png)\n\n### Runners\n\n![help](https://github.com/INSRapperswil/gitlabtree/blob/main/doc/imgs/gitlabtree_runners.png)\n\n### Visibility\n\n![help](https://github.com/INSRapperswil/gitlabtree/blob/main/doc/imgs/gitlabtree_visibility.png)\n\n',
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
