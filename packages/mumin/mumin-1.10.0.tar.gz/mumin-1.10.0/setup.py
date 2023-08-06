# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mumin']

package_data = \
{'': ['*']}

install_requires = \
['newspaper3k>=0.2.8,<0.3.0',
 'pandas>=1.4.3,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'torch>=1.12.0,<2.0.0',
 'tqdm>=4.62.0,<5.0.0',
 'transformers>=4.20.0,<5.0.0',
 'wrapt-timeout-decorator>=1.3.12,<2.0.0']

setup_kwargs = {
    'name': 'mumin',
    'version': '1.10.0',
    'description': 'Seamlessly build the MuMiN dataset.',
    'long_description': "# MuMiN-Build\nThis repository contains the package used to build the MuMiN dataset from the\npaper [Nielsen and McConville: _MuMiN: A Large-Scale Multilingual Multimodal\nFact-Checked Misinformation Social Network Dataset_\n(2021)](https://arxiv.org/abs/2202.11684).\n\nSee [the MuMiN website](https://mumin-dataset.github.io/) for more information,\nincluding a leaderboard of the top performing models.\n\n______________________________________________________________________\n[![PyPI Status](https://badge.fury.io/py/mumin.svg)](https://pypi.org/project/mumin/)\n[![Documentation](https://img.shields.io/badge/docs-passing-green)](https://mumin-dataset.github.io/mumin-build/mumin.html)\n[![License](https://img.shields.io/github/license/mumin-dataset/mumin-build)](https://github.com/mumin-dataset/mumin-build/blob/main/LICENSE)\n[![LastCommit](https://img.shields.io/github/last-commit/mumin-dataset/mumin-build)](https://github.com/mumin-dataset/mumin-build/commits/main)\n[![Code Coverage](https://img.shields.io/badge/Coverage-76%25-yellowgreen.svg)](https://github.com/mumin-dataset/mumin-build/tree/dev/tests)\n\n\n## Installation\nThe `mumin` package can be installed using `pip`:\n```\n$ pip install mumin\n```\n\nTo be able to build the dataset, Twitter data needs to be downloaded, which\nrequires a Twitter API key. You can get one\n[for free here](https://developer.twitter.com/en/portal/dashboard). You will\nneed the _Bearer Token_.\n\n\n## Quickstart\nThe main class of the package is the `MuminDataset` class:\n```\n>>> from mumin import MuminDataset\n>>> dataset = MuminDataset(twitter_bearer_token=XXXXX)\n>>> dataset\nMuminDataset(size='small', compiled=False)\n```\n\nBy default, this loads the small version of the dataset. This can be changed by\nsetting the `size` argument of `MuminDataset` to one of 'small', 'medium' or\n'large'. To begin using the dataset, it first needs to be compiled. This will\ndownload the dataset, rehydrate the tweets and users, and download all the\nassociated news articles, images and videos. This usually takes a while.\n```\n>>> dataset.compile()\nMuminDataset(num_nodes=388,149, num_relations=475,490, size='small', compiled=True)\n```\n\nNote that this dataset does not contain _all_ the nodes and relations in\nMuMiN-small, as that would take way longer to compile. The data left out are\ntimelines, profile pictures and article images. These can be included by\nspecifying `include_extra_images=True` and/or `include_timelines=True` in the\nconstructor of `MuminDataset`.\n\nAfter compilation, the dataset can also be found in the `mumin-<size>.zip`\nfile. This file name can be changed using the `dataset_path` argument when\ninitialising the `MuminDataset` class. If you need embeddings of the nodes, for\ninstance for use in machine learning models, then you can simply call the\n`add_embeddings` method:\n```\n>>> dataset.add_embeddings()\nMuminDataset(num_nodes=388,149, num_relations=475,490, size='small', compiled=True)\n```\n\n**Note**: If you need to use the `add_embeddings` method, you need to install\nthe `mumin` package as either `pip install mumin[embeddings]` or `pip install\nmumin[all]`, which will install the `transformers` and `torch` libraries. This\nis to ensure that such large libraries are only downloaded if needed.\n\nIt is possible to export the dataset to the\n[Deep Graph Library](https://www.dgl.ai/), using the `to_dgl` method:\n```\n>>> dgl_graph = dataset.to_dgl()\n>>> type(dgl_graph)\ndgl.heterograph.DGLHeteroGraph\n```\n\n**Note**: If you need to use the `to_dgl` method, you need to install the\n`mumin` package as `pip install mumin[dgl]` or `pip install mumin[all]`, which\nwill install the `dgl` and `torch` libraries.\n\nFor a more in-depth tutorial of how to work with the dataset, including\ntraining multiple different misinformation classifiers, see [the\ntutorial](https://colab.research.google.com/drive/1Kz0EQtySYQTo1ui8F2KZ6ERneZVf5TIN).\n\n\n## Dataset Statistics\n\n| Dataset | #Claims | #Threads | #Tweets | #Users | #Articles | #Images | #Languages | %Misinfo |\n| ---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n| MuMiN-large | 12,914 | 26,048 | 21,565,018 | 1,986,354 | 10,920 | 6,573 | 41 | 94.57% |\n| MuMiN-medium | 5,565 | 10,832 | 12,650,371 | 1,150,259 | 4,212 | 2,510 | 37 | 94.07% |\n| MuMiN-small | 2,183 | 4,344 | 7,202,506 | 639,559 | 1,497 | 1,036 | 35 | 92.87% |\n\n\n## Related Repositories\n- [MuMiN website](https://mumin-dataset.github.io/), the central place for the\n  MuMiN ecosystem, containing tutorials, leaderboards and links to the paper\n  and related repositories.\n- [MuMiN](https://github.com/MuMiN-dataset/mumin), containing the\n  paper in PDF and LaTeX form.\n- [MuMiN-trawl](https://github.com/MuMiN-dataset/mumin-trawl),\n  containing the source code used to construct the dataset from scratch.\n- [MuMiN-baseline](https://github.com/MuMiN-dataset/mumin-baseline),\n  containing the source code for the baselines.\n",
    'author': 'Dan Saattrup Nielsen',
    'author_email': 'dan.nielsen@alexandra.dk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://mumin-dataset.github.io/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
