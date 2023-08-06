# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scyan', 'scyan.data', 'scyan.module', 'scyan.plot']

package_data = \
{'': ['*']}

install_requires = \
['FlowIO>=1.0.1,<2.0.0',
 'FlowUtils>=1.0.0,<2.0.0',
 'llvmlite>=0.38.1,<0.39.0',
 'matplotlib>=3.5.2,<4.0.0',
 'pytorch-lightning>=1.6.4,<2.0.0',
 'scanpy>=1.9.1,<2.0.0',
 'scikit-learn>=1.1.1,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'umap-learn>=0.5.3,<0.6.0']

extras_require = \
{'dev': ['wandb>=0.12.20,<0.13.0',
         'hydra-core>=1.2.0,<2.0.0',
         'hydra-colorlog>=1.2.0,<2.0.0',
         'hydra-optuna-sweeper>=1.2.0,<2.0.0',
         'pytest>=7.1.2,<8.0.0',
         'ipykernel>=6.15.0,<7.0.0',
         'ipywidgets>=7.7.1,<8.0.0',
         'isort>=5.10.1,<6.0.0',
         'black>=22.6.0,<23.0.0',
         'imblearn>=0.0,<0.1'],
 'discovery': ['leidenalg>=0.8.10,<0.9.0'],
 'docs': ['mkdocs-material>=8.3.9,<9.0.0',
          'mkdocstrings>=0.19.0,<0.20.0',
          'mkdocstrings-python>=0.7.1,<0.8.0',
          'mkdocs-jupyter>=0.21.0,<0.22.0']}

setup_kwargs = {
    'name': 'scyan',
    'version': '0.1.1',
    'description': 'Single-cell Cytometry Annotation Network',
    'long_description': '<p align="center">\n  <img src="https://github.com/MICS-Lab/scyan/raw/master/docs/assets/logo.png" alt="scyan_logo" width="500"/>\n</p>\n\nScyan stands for **S**ingle-cell **Cy**tometry **A**nnotation **N**etwork. Based on biological knowledge prior, it provides a fast cell population annotation without requiring any training label. Scyan is an interpretable model that also corrects batch-effect and can be used for debarcoding / cell sampling / population discovery.\n\n# Documentation\n\nThe [complete documentation can be found here](https://mics_biomathematics.pages.centralesupelec.fr/biomaths/scyan/). It contains installation guidelines, tutorials, a description of the API, etc.\n\n# Overview\n\nScyan is a Bayesian probabilistic model composed of a deep invertible neural network called a normalizing flow (the function $f_{\\phi}$). It maps a latent distribution of cell expressions into the empirical distribution of cell expressions. This cell distribution is a mixture of gaussian-like distributions representing the sum of a cell-specific and a population-specific term. Also, interpretability and batch effect correction are based on the model latent space — more details in the article\'s Methods section.\n\n<p align="center">\n  <img src="https://github.com/MICS-Lab/scyan/raw/master/docs/assets/overview.png" alt="overview_image"/>\n</p>\n\n# Getting started\n\nScyan can be installed on every OS with `pip` or [`poetry`](https://python-poetry.org/docs/).\n\nOn MacOS / Linux, `python>=3.8,<3.11` is required, while `python>=3.8,<3.10` is required on Windows. The preferred Python version is `3.9`.\n\n## Install with PyPI\n\nAvailable after publication\n\n## Install locally\n\n> Advice (optional): We advise creating a new environment via a package manager (except if you use Poetry, which will automatically create the environment). For instance, you can create a new `conda` environment:\n>\n> ```bash\n> conda create --name scyan python=3.9\n> conda activate scyan\n> ```\n\nClone the repository and move to its root:\n\n```bash\ngit clone https://github.com/MICS-Lab/scyan.git\ncd scyan\n```\n\nChoose one of the following, depending on your needs (it should take at most a few minutes):\n\n```bash\npip install .                           # pip minimal installation (library only)\npip install -e \'.[dev,docs,discovery]\'  # pip installation in editable mode\npoetry install -E \'dev docs discovery\'  # poetry installation in editable mode\n```\n\n## Basic usage\n\n```py\nimport scyan\n\nadata, marker_pop_matrix = scyan.data.load("aml")\n\nmodel = scyan.Scyan(adata, marker_pop_matrix)\nmodel.fit()\nmodel.predict()\n```\n\nThis code should run in approximately 40 seconds (once the dataset was loaded).\nFor more usage demo, read the [tutorials](https://mics_biomathematics.pages.centralesupelec.fr/biomaths/scyan/tutorials/usage/) or the complete [documentation](https://mics_biomathematics.pages.centralesupelec.fr/biomaths/scyan/).\n\n# Technical description\n\nScyan is a **Python** library based on:\n\n- _Pytorch_, a deep learning framework\n- _AnnData_, a data library that works nicely with single-cell data\n- _Pytorch Lighning_, for model training\n- _Hydra_, for project configuration (optional)\n- _Weight & Biases_, for model monitoring (optional)\n\n# Project layout\n\n    config/       # Hydra configuration folder (optional use)\n    data/         # Data folder containing adata files and csv tables\n    docs/         # The folder used to build the documentation\n    scripts/      # Scripts to reproduce the results from the article\n    tests/        # Folder containing tests\n    scyan/                    # Library source code\n        data/                 # Folder with data-related functions and classes\n            datasets.py       # Load and save datasets\n            tensors.py        # Pytorch data related classes for training\n        module/               # Folder containing neural network modules\n            coupling_layer.py # Coupling layer\n            distribution.py   # Prior distribution (called U in the article)\n            real_nvp.py       # Normalizing Flow\n            scyan_module      # Core module\n        plot/                 # Plotting tools\n            ...\n        mmd.py                # Maximum Mean Discrepancy implementation\n        model.py              # Scyan model class\n        preprocess.py         # Preprocessing functions\n        utils.py              # Misc functions\n    .gitattributes\n    .gitignore\n    .gitlab-ci.yml    # CI that builds documentation\n    CONTRIBUTING.md   # To read before contributing\n    LICENSE\n    mkdocs.yml        # The docs configuration file\n    poetry.lock\n    pyproject.toml    # Dependencies, project metadata, and more\n    README.md\n    setup.py          # Setup file, see `pyproject.toml`\n',
    'author': 'Blampey Quentin',
    'author_email': 'quentin.blampey@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://mics_biomathematics.pages.centralesupelec.fr/biomaths/scyan/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
