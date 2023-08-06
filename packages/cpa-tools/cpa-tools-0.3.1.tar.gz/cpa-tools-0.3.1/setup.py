# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cpa']

package_data = \
{'': ['*']}

install_requires = \
['anndata>=0.7.5',
 'llvmlite>=0.38.0,<0.39.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.21.5,<2.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'scvi-tools>=0.16.4',
 'seaborn>=0.11.2,<0.12.0']

extras_require = \
{':(python_version < "3.8") and (extra == "docs")': ['typing_extensions'],
 ':extra == "dev" or extra == "docs" or extra == "tutorials"': ['scanpy>=1.6'],
 ':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0'],
 'dev': ['black>=20.8b1',
         'codecov>=2.0.8',
         'flake8>=3.7.7',
         'isort>=5.7',
         'jupyter>=1.0',
         'loompy>=3.0.6',
         'nbconvert>=5.4.0',
         'nbformat>=4.4.0',
         'pre-commit>=2.7.1',
         'pytest>=4.4'],
 'docs': ['ipython>=7.1.1',
          'nbsphinx',
          'nbsphinx-link',
          'pydata-sphinx-theme>=0.4.0',
          'scanpydoc>=0.5',
          'sphinx>=4.1,<4.4',
          'sphinx-autodoc-typehints',
          'sphinx-rtd-theme'],
 'tutorials': ['leidenalg',
               'loompy>=3.0.6',
               'python-igraph',
               'scikit-misc>=0.1.3']}

setup_kwargs = {
    'name': 'cpa-tools',
    'version': '0.3.1',
    'description': 'Compositional Perturbation Autoencoder (CPA)',
    'long_description': '# CPA - Compositional Perturbation Autoencoder\n\n\n## What is CPA?\n\n![Alt text](https://user-images.githubusercontent.com/33202701/156530222-c61e5982-d063-461c-b66e-c4591d2d0de4.png?raw=true "Title")\n\n`CPA` is a framework to learn effects of perturbations at the single-cell level. CPA encodes and learns phenotypic drug response across different cell types, doses and drug combinations. CPA allows:\n\n* Out-of-distribution predictions of unseen drug combinations at various doses and among different cell types.\n* Learn interpretable drug and cell type latent spaces.\n* Estimate dose response curve for each perturbation and their combinations.\n* Access the uncertainty of the estimations of the model.\n\n\nUsage and installation\n-------------------------------\nSee [here](https://cpa-tools.readthedocs.io/en/latest/index.html) for documentation and tutorials.\n\nSupport and contribute\n-------------------------------\nIf you have a question or new architecture or a model that could be integrated into our pipeline, you can\npost an [issue](https://github.com/theislab/cpa/issues/new)\n\n\n###### Acknowledgment\nThis code is inspired by an early implementatiom by [Pierre Boyeau](https://github.com/PierreBoyeau) using [scvi-tools](https://scvi-tools.org/).\n\n',
    'author': 'Mohsen Naghipourfar',
    'author_email': 'naghipourfar@berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theislab/cpa/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.2,<3.11',
}


setup(**setup_kwargs)
