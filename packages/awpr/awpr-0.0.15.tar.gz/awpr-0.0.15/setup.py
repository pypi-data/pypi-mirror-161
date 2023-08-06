# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['awpr']

package_data = \
{'': ['*']}

install_requires = \
['beartype>=0.10.4,<0.11.0', 'loguru>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'awpr',
    'version': '0.0.15',
    'description': 'Library that helps an application report progress to Argo Workflows.',
    'long_description': '# awpr\nLibrary that helps an application report progress to Argo Workflows.\n\n\n## Installation \n```shell\npip install awpr\n```\n\n## Usage\nSet the environment variable and run your application:\n`ARGO_PROGRESS_FILE=/tmp/progress.txt`\n\n```shell\nfrom awpr.awpr import ArgoWorkflowsProgressReporter\n\nawpr = ArgoWorkflowsProgressReporter()\nawpr.set_total_progress(100)\nawpr.start_reporting()\n\nawpr.set_current_progress(20)\nawpr.set_current_progress(30)\nawpr.get_progress_percent()\n```',
    'author': 'Michael Mohamed',
    'author_email': 'michael@foundationstack.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fsai-dev/fsai-cli-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
