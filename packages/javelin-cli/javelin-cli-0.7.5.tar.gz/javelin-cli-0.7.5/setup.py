# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['javelin', 'javelin.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0',
 'PyYAML>=6.0,<7.0',
 'boto3>=1.24.14,<2.0.0',
 'packaging>=21.3,<22.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'python-semantic-release>=7.29.2,<8.0.0',
 'slack-sdk>=3.17.2,<4.0.0']

setup_kwargs = {
    'name': 'javelin-cli',
    'version': '0.7.5',
    'description': 'CLI tool for managing Spearly deployments.',
    'long_description': '# Javelin\n\nCLI tool for managing Spearly deployments.\n\n## Requirements\n- Python 3.10+\n- `GITHUB_ACCESS_TOKEN` environment variable set to a **GitHub Personal Access Token** with `repo` scope ([Ref](https://github.com/settings/tokens))\n- **AWS IAM User** with `codepipeline:StartPipelineExecution` permission to the required resources ([Ref](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration))\n\n## Installation\n```sh\nbrew install pyenv\npyenv install\npip install javelin-cli\n```\n\n## Usage\n```sh\npython -m javelin --help\n```\n',
    'author': 'David Grilli',
    'author_email': 'dj@unimal.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/unimal-jp/javelin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
