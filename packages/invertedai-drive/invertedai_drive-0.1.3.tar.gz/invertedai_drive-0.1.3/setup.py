# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['invertedai_drive']

package_data = \
{'': ['*']}

install_requires = \
['numpy==1.21.2', 'python-dotenv>=0.20.0,<0.21.0', 'torch>=1.11.0,<2.0.0']

setup_kwargs = {
    'name': 'invertedai-drive',
    'version': '0.1.3',
    'description': 'Client SDK for InvertedAI Drive',
    'long_description': '# InvertedAI Drive\n\n## Getting Started\n\n### Running demo locally\n\nDownload the examples [directory](https://github.com/inverted-ai/invertedai-drive/blob/master/examples) and run:\n\n```\npython -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\n.venv/bin/jupyter notebook Drive-Demo.ipynb\n```\n\n### Running demo in [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/inverted-ai/invertedai-drive/blob/develop/examples/Colab-Demo.ipynb)\n',
    'author': 'Inverted AI',
    'author_email': 'info@inverted.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
