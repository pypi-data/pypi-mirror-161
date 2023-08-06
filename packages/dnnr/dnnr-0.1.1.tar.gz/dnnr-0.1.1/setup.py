# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dnnr', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['annoy>=1.17.0,<2.0.0',
 'numpy>=1.21.0,<2.0.0',
 'scikit-learn>=1.0.0,<2.0.0',
 'scipy>=1.7.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'dnnr',
    'version': '0.1.1',
    'description': 'Easy to use package of the DNNR regression.',
    'long_description': "# DNNR: Differential Nearest Neighbors Regression\n\n[![Build Status](https://github.com/younader/dnnr/actions/workflows/dev.yml/badge.svg)](https://github.com/younader/dnnr/actions/workflows/dev.yml)\n\n[[Paper](https://proceedings.mlr.press/v162/nader22a.html)]\n[[Documentation](https://younader.github.io/dnnr/)]\n\nThe Python package of [differential nearest neighbors regression (DNNR)](https://proceedings.mlr.press/v162/nader22a.html): **Raising KNN-regression to levels of gradient boosting methods.**\n\nWhereas KNN regression only uses the averaged value, DNNR also uses the gradient or even higher-order derivatives:\n\n![KNN and DNNR Overview Image](knn_dnnr_overview.png)\n\nOur implementation uses `numpy`, `sklearn`, and the [`annoy`](https://github.com/spotify/annoy) approximate nearest neighbor index. Using `annoy` is optional, as you can also use `sklearn`'s KDTree as index. We support Python 3.7 to 3.10.\n\n\n# 🚀 Quickstart\n\n\nTo install this project, run:\n\n```bash\npip install dnnr\n```\n\n\n# 🎉 Example\n\n```python\nimport numpy as np\nfrom dnnr import DNNR\n\nX = np.array([[0], [1], [2], [3]])\ny = np.array([0, 0, 1, 1])\n\nmodel = DNNR(n_neighbors=1, n_derivative_neighbors=3)\nmodel.fit(X, y)\nmodel.predict([[1.5]])\n# Will output: 0.25\n```\n\nAlso check out our [Jupiter Notebook](./examples/dnnr_tutorial.ipynb) on how to use DNNR. [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/younader/dnnr/blob/main/examples/dnnr_tutorial.ipynb)\n\n\n# 📊 Hyperparameters\n\nDNNR has three main hyperparameters:\n\n* `n_neighbors`: number of nearest neighbors to use. The default value of\n      `3` is usually a good choice.\n* `n_derivative_neighbors`: number of neighbors used in approximating the\n      derivatives. As a default value, we choose `3 * dim`, where `dim` is\n      the input dimension.\n* `order`: Taylor approximation order, one of `1`, `2`, `2diag`, `3diag`.\n      The preferable option here is `1`. Sometimes `2diag` can deliver\n      small improvements. `2` and `3diag` are implemented but usually do\n      not yield significant improvements.\n\nWe recommend a hyperparameter search over the `n_derivative_neighbors` variable to archive the best performance.\n\nFor all options, see the [documentation of the DNNR class](https://younader.github.io/dnnr/api/#dnnr.dnnr.DNNR).\n\n#  🛠 Development Installation\n\n```bash\npython3 -m venv venv      # create a virtual environment\nsource venv/bin/activate  # and load it\ngit clone https://github.com/younader/dnnr.git\ncd dnnr\npip install -U pip wheel poetry\npoetry install\nmake test                 # to run the tests\n```\n\n\n# 📄 Citation\n\nIf you use this library for a scientific publication, please use the following BibTex entry to cite our work:\n\n```bibtex\n@InProceedings{pmlr-v162-nader22a,\n  title = \t {{DNNR}: Differential Nearest Neighbors Regression},\n  author =       {Nader, Youssef and Sixt, Leon and Landgraf, Tim},\n  booktitle = \t {Proceedings of the 39th International Conference on Machine Learning},\n  pages = \t {16296--16317},\n  year = \t {2022},\n  editor = \t {Chaudhuri, Kamalika and Jegelka, Stefanie and Song, Le and Szepesvari, Csaba and Niu, Gang and Sabato, Sivan},\n  volume = \t {162},\n  series = \t {Proceedings of Machine Learning Research},\n  month = \t {17--23 Jul},\n  publisher =    {PMLR},\n  pdf = \t {https://proceedings.mlr.press/v162/nader22a/nader22a.pdf},\n  url = \t {https://proceedings.mlr.press/v162/nader22a.html},\n}\n```\n",
    'author': 'Youssef Nadar',
    'author_email': 'youssef.nadar@fu-berlin.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/younader/dnnr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
