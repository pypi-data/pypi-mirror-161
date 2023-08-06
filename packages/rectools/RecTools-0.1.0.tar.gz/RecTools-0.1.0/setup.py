# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['rectools',
 'rectools.dataset',
 'rectools.metrics',
 'rectools.model_selection',
 'rectools.models',
 'rectools.tools',
 'rectools.utils']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.2,<3.3',
 'attrs>=19.1.0,<22.0.0',
 'implicit==0.4.4',
 'lightfm>=1.16,<2.0',
 'nmslib>=2.0.4,<3.0.0',
 'numpy>=1.19.5,<2.0.0',
 'pandas>=0.25.3,<2.0.0',
 'scipy>=1.5.4,<2.0.0',
 'tqdm>=4.27.0,<5.0.0',
 'typeguard>=2.0.1,<3.0.0']

extras_require = \
{'all': ['torch>=1.6,<2.0', 'pytorch-lightning>=1.6,<2.0'],
 'nn': ['torch>=1.6,<2.0', 'pytorch-lightning>=1.6,<2.0']}

setup_kwargs = {
    'name': 'rectools',
    'version': '0.1.0',
    'description': 'An easy-to-use Python library for building recommendation systems',
    'long_description': '# RecTools\n\n[![Python versions](https://img.shields.io/pypi/pyversions/rectools.svg)](https://pypi.org/project/rectools)\n[![PyPI](https://img.shields.io/pypi/v/rectools.svg)](https://pypi.org/project/rectools)\n[![Docs](https://img.shields.io/github/workflow/status/MobileTeleSystems/RecTools/Publish?label=docs)](https://rectools.readthedocs.io)\n\n[![License](https://img.shields.io/github/license/MobileTeleSystems/RecTools.svg)](https://github.com/MobileTeleSystems/RecTools/blob/main/LICENSE)\n[![Coverage](https://img.shields.io/codecov/c/github/MobileTeleSystems/RecTools.svg)](https://app.codecov.io/gh/MobileTeleSystems/RecTools)\n[![Tests](https://img.shields.io/github/workflow/status/MobileTeleSystems/RecTools/Test/main?label=tests)](https://github.com/MobileTeleSystems/RecTools/actions/workflows/test.yml?query=branch%3Amain++)\n\n[![Contributors](https://img.shields.io/github/contributors/MobileTeleSystems/RecTools.svg)](https://github.com/MobileTeleSystems/RecTools/graphs/contributors)\n[![Telegram](https://img.shields.io/badge/channel-telegram-blue)](https://t.me/RecTools_Support)\n\nRecTools is an easy-to-use Python library which makes the process of building recommendation systems easier, \nfaster and more structured than ever before.\nIt includes built in toolkits for data processing and metrics calculation, \na variety of recommender models, some wrappers for already existing implementations of popular algorithms \nand model selection framework.\nThe aim is to collect ready-to-use solutions and best practices in one place to make processes \nof creating your first MVP and deploying model to production as fast and easy as possible.\n\nRecTools allows to easily work with dense and sparse features.\nIt features such basic models as ones based on random suggestions or popularity and more advanced ones, e.g. LightFM.\nIt also contains a wide variety of metrics to choose from to better suit recommender system to your needs.\n\nFor more details, see the [Documentation](https://rectools.readthedocs.io/) \nand [Tutorials](https://github.com/MobileTeleSystems/RecTools/tree/main/examples).\n\n## Get started\n\nPrepare data with\n\n```shell\nwget https://files.grouplens.org/datasets/movielens/ml-1m.zip\nunzip ml-1m.zip\n```\n\n```python\nimport pandas as pd\nfrom implicit.nearest_neighbours import TFIDFRecommender\n    \nfrom rectools import Columns\nfrom rectools.dataset import Dataset\nfrom rectools.models import ImplicitItemKNNWrapperModel\n\n# Read the data\nratings = pd.read_csv(\n    "ml-1m/ratings.dat", \n    sep="::",\n    engine="python",  # Because of 2-chars separators\n    header=None,\n    names=[Columns.User, Columns.Item, Columns.Weight, Columns.Datetime],\n)\n    \n# Create dataset\ndataset = Dataset.construct(ratings)\n    \n# Fit model\nmodel = ImplicitItemKNNWrapperModel(TFIDFRecommender(K=10))\nmodel.fit(dataset)\n\n# Make recommendations\nrecos = model.recommend(\n    users=ratings[Columns.User].unique(),\n    dataset=dataset,\n    k=10,\n    filter_viewed=True,\n)\n```\n\n## Installation\n\nRecTools is on PyPI, so you can use `pip` to install it.\n```\npip install rectools\n```\n\n\n## Contribution\n\nTo install all requirements run\n```\nmake install\n```\nYou must have `python3` and `poetry` installed.\n\nFor autoformatting run \n```\nmake autoformat\n```\n\nFor linters check run \n```\nmake lint\n```\n\nFor tests run \n```\nmake test\n```\n\nFor coverage run \n```\nmake coverage\n```\n\nTo remove virtual environment run\n```\nmake clean\n```\n',
    'author': 'Daniil Potapov',
    'author_email': 'sharth23@gmail.com',
    'maintainer': 'Daniil Potapov',
    'maintainer_email': 'sharth23@gmail.com',
    'url': 'https://github.com/MobileTeleSystems/RecTools',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.10.0',
}


setup(**setup_kwargs)
