# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autotst']

package_data = \
{'': ['*']}

install_requires = \
['autogluon>=0.4.2,<0.5.0',
 'importlib-metadata>=1.4',
 'nptyping>=1.4.4,<2.0.0',
 'numpy>=1.21,<2.0',
 'pandas>=1.3,<2.0',
 'pytest>=7.1.2,<8.0.0',
 'torchvision==0.11.3']

setup_kwargs = {
    'name': 'autotst',
    'version': '1.2',
    'description': 'Two-samples Testing and Distribution Shift Detection with AutoML',
    'long_description': '# AutoML Two-Sample Test\n\n[![Checked with MyPy](https://img.shields.io/badge/mypy-checked-blue)](https://github.com/python/mypy)\n[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Tests](https://github.com/jmkuebler/auto-tst/actions/workflows/tests.yml/badge.svg)](https://github.com/jmkuebler/auto-tst/actions/workflows/tests.yml)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![PyPI](https://img.shields.io/badge/PyPI-1.2-blue)](https://pypi.org/project/autotst/)\n[![Downloads](https://static.pepy.tech/personalized-badge/autotst?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/autotst)\n[![arXiv](https://img.shields.io/badge/arXiv-2206.08843-b31b1b.svg)](https://arxiv.org/abs/2206.08843) \n\n`autotst` is a Python package for easy-to-use two-sample testing and distribution shift detection.\n\nGiven two datasets `sample_P` and `sample_Q` drawn from distributions $P$ and $Q$, the \ngoal is to estimate a $p$-value for the null hypothesis $P=Q$.\n`autotst` achieves this by learning a witness function and taking its mean discrepancy as a test statistic\n(see References).\n\nThe package provides functionalities to prepare the data, an interface to train an ML model, and methods\nto evaluate $p$-values and interpret results.\n\nBy default, autotst uses the Tabular Predictor of [AutoGluon](https://auto.gluon.ai/), but it is easy \nto wrap and use your own favorite ML framework (see below).\n\nThe full documentation of the package can be found [here](https://jmkuebler.github.io/auto-tst/).\n\n## Installation\nRequires at least Python 3.7. Since the installation also installs AutoGluon, it can take a few moments.\n```\npip install autotst\n```\n\n## How to use `autotst`\nWe provide worked out examples in the \'Example\' directory. In the following assume that\n`sample_P` and `sample_Q` are two `numpy` arrays containing samples from $P$ and $Q$. \n\n### Default Usage:\n\nThe easiest way to compute a $p$-value is to use the default settings\n```python\nimport autotst\ntst = autotst.AutoTST(sample_P, sample_Q)\np_value = tst.p_value()\n```\nYou would then reject the null hypothesis if `p_value` is smaller or equal to your significance level.\n\n### Customizing the testing pipeline\nWe highly recommend to use the pipeline step by step, which would look like this:\n```python\nimport autotst\nfrom autotst.model import AutoGluonTabularPredictor\n\ntst = autotst.AutoTST(sample_P, sample_Q, split_ratio=0.5, model=AutoGluonTabularPredictor)\ntst.split_data()\ntst.fit_witness(time_limit=60)  # time limit adjustable to your needs (in seconds)\np_value = tst.p_value_evaluate(permutations=10000)  # control number of permutations in the estimation\n```\nThis allows you to change the time limit for fitting the witness function and you can also pass other \narguments to the fit model (see [AutoGluon](https://auto.gluon.ai/) documentation).\n\nSince the permutations are very cheap, the default number of permutations is relatively high and should work for most\nuse-cases. If your significance level is, say, smaller than 1/1000, consider increasing it further.\n\n### Customizing the machine learning model\nIf you have good domain knowledge about your problem and believe that a specific ML framework will work well,\nit is easy to wrap your model. \nTherefore, simply inherit from the class `Model` and wrap the methods\n(see our implementation in [`model.py`](autotst/model.py)).\n\nYou can then run the test simply by importing your model and initializing the test accordingly.\n\n```python\nimport autotst\n\ntst = autotst.AutoTST(sample_P, sample_Q, model=YourCustomModel)\n...\n... etc.\n```\n\nWe also provide a wrapper for `AutoGluonImagePredictor`. However, it seems that this should not be used \nwith small datasets and small training times.\n\n## References\nIf you use this package, please cite this paper:\n\nJonas M. Kübler, Vincent Stimper, Simon Buchholz, Krikamol Muandet, Bernhard Schölkopf: "AutoML Two-Sample Test", [arXiv 2206.08843](https://arxiv.org/abs/2206.08843) (2022)\n\nBibtex:\n```\n@misc{kubler2022autotst,\n  doi = {10.48550/ARXIV.2206.08843},\n  url = {https://arxiv.org/abs/2206.08843},\n  author = {Kübler, Jonas M. and Stimper, Vincent and Buchholz, Simon and Muandet, Krikamol and Schölkopf, Bernhard},  \n  title = {AutoML Two-Sample Test},\n  publisher = {arXiv},\n  year = {2022},\n}\n```\n',
    'author': 'Jonas M. Kübler',
    'author_email': 'jonas.m.kuebler@tuebingen.mpg.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://jmkuebler.github.io/auto-tst/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
