# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bamt',
 'bamt.external',
 'bamt.external.libpgm',
 'bamt.external.pyBN',
 'bamt.external.pyBN.classes',
 'bamt.external.pyBN.classes._tests',
 'bamt.external.pyBN.classification',
 'bamt.external.pyBN.inference',
 'bamt.external.pyBN.inference._tests',
 'bamt.external.pyBN.inference.map_exact',
 'bamt.external.pyBN.inference.marginal_approx',
 'bamt.external.pyBN.inference.marginal_exact',
 'bamt.external.pyBN.io',
 'bamt.external.pyBN.io._tests',
 'bamt.external.pyBN.learning',
 'bamt.external.pyBN.learning.parameter',
 'bamt.external.pyBN.learning.parameter._tests',
 'bamt.external.pyBN.learning.structure',
 'bamt.external.pyBN.learning.structure._tests',
 'bamt.external.pyBN.learning.structure.constraint',
 'bamt.external.pyBN.learning.structure.exact',
 'bamt.external.pyBN.learning.structure.hybrid',
 'bamt.external.pyBN.learning.structure.naive',
 'bamt.external.pyBN.learning.structure.score',
 'bamt.external.pyBN.learning.structure.tree',
 'bamt.external.pyBN.plotting',
 'bamt.external.pyBN.utils',
 'bamt.external.pyBN.utils._tests',
 'bamt.preprocess',
 'bamt.utils']

package_data = \
{'': ['*']}

install_requires = \
['gmr==1.6.2',
 'matplotlib==3.5.1',
 'missingno>=0.5.1,<0.6.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas==1.4.0',
 'pgmpy>=0.1.17,<0.2.0',
 'pomegranate==0.14.8',
 'pyitlib>=0.2.2,<0.3.0',
 'pyvis>=0.1.9,<0.2.0',
 'scikit-learn==1.0.2',
 'scipy>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'bamt',
    'version': '1.1.24',
    'description': 'data modeling and analysis tool based on Bayesian networks',
    'long_description': "# BAMT\nRepository of a data modeling and analysis tool based on Bayesian networks\n\n\nBAMT - Bayesian Analytical and Modelling Toolkit. This repository contains a data modeling and analysis tool based on Bayesian networks. It can be divided into two main parts - algorithms for constructing and training Bayesian networks on data and algorithms for applying Bayesian networks for filling gaps, generating synthetic data, and searching for anomalous values.\n\n### Installation\n\nBAMT package is available via PyPi: ``pip install bamt``\n\nBayesian network learning\n=========================\nIn terms of training Bayesian networks on data, the following algorithms are implemented:\n- Building the structure of a Bayesian network based on expert knowledge by directly specifying the structure of the network;\n- Building the structure of a Bayesian network on data using three algorithms - Hill Climbing, evolutionary and PC. For Hill Climbing, the following score functions are implemented - MI, K2, BIC, AIC. The algorithms work on both discrete and mixed data.\n- Training the parameters of distributions in the nodes of the network on the basis of data.\n\nDifference from existing implementations:\n- Algorithms work on mixed data;\n- Structural learning implements score-functions for mixed data;\n- Parametric learning implements the use of a mixture of Gaussian distributions to approximate continuous distributions;\n- The algorithm for structural training of large Bayesian networks (> 10 nodes) is based on local training of small networks with their subsequent algorithmic connection.\n![title](img/BN_gif.gif)\n\nGenerating synthetic data\n=========================\nIn terms of data analysis and modeling using Bayesian networks, a pipeline has been implemented to generate synthetic data by sampling from Bayesian networks.\n![title](img/synth_gen.png)\n\nOil and Gas Reservoirs Parameters Analysis\n==========================================\nBayesian networks can be used to restore gaps in reservoirs data, search for anomalous values, and also to search for analogous reservoirs.\n![title](img/concept.png)\n\n# Project structure\n## Utils\n  1. GraphUtils consist of functions for:\n  - Finding nodes types/signs\n  - Topological ordering\n  2. MathUtils consist of functions for:\n  - Additional function to support calculation of metrics from group1 ('MI', 'LL', 'BIC', 'AIC')\n\n## Preprocessing\nPreprocessor module allows user to transform data according pipeline (in analogy with pipeline in scikit-learn).\n## Networks\nThere are 3 general types of networks: discrete, gaussian, hybrid. All implemented in networks.py  \n## Nodes\nContains nodes' classes and their methods.\n",
    'author': 'Roman Netrogolov',
    'author_email': 'romius2001@gmail.com',
    'maintainer': 'N Mramorov',
    'maintainer_email': None,
    'url': 'https://github.com/ITMO-NSS-team/BAMT',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
