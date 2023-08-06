# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['summit',
 'summit.benchmarks',
 'summit.benchmarks.MIT',
 'summit.strategies',
 'summit.tests',
 'summit.utils']

package_data = \
{'': ['*'],
 'summit.benchmarks': ['data/*',
                       'models/baumgartner_aniline_cn_crosscoupling/*',
                       'models/baumgartner_aniline_cn_crosscoupling_descriptors/*',
                       'models/reizman_suzuki_case_1/*',
                       'models/reizman_suzuki_case_2/*',
                       'models/reizman_suzuki_case_3/*',
                       'models/reizman_suzuki_case_4/*']}

install_requires = \
['GPy>=1.9,<2.0',
 'SQSnobFit>=0.4.3,<0.5.0',
 'botorch>=0.5.0,<0.6.0',
 'cython>=0.29.21,<0.30.0',
 'fastprogress>=0.2.3,<0.3.0',
 'gpyopt>=1.2.6,<2.0.0',
 'gpytorch>=1.5.0,<2.0.0',
 'llvmlite>=0.38.0,<0.39.0',
 'matplotlib>=3.2.2,<4.0.0',
 'numba>=0.55.0,<0.56.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.1.0,<2.0.0',
 'pymoo>=0.4.1,<0.5.0',
 'pyrff>=2.0.1,<3.0.0',
 'pytest>=6.2.5,<7.0.0',
 'scikit-learn>=1.0,<2.0',
 'scipy>=1.8.0',
 'skorch>=0.9.0,<0.10.0',
 'torch>=1.4.0,<2.0.0']

extras_require = \
{'docs': ['sphinx>=3.2.1,<4.0.0',
          'jinja2<3.1.0',
          'nbsphinx>=0.8.5,<0.9.0',
          'sphinx-rtd-theme>=0.5.0,<0.6.0',
          'sphinx-reredirects>=0.0.0,<0.0.1'],
 'entmoot': ['entmoot>=0.1.4,<0.2.0'],
 'experiments': ['xlrd>=1.2.0,<2.0.0',
                 'streamlit>=0.67.1,<0.68.0',
                 'neptune-client>=0.4.115,<0.5.0',
                 'hiplot>=0.1.12,<0.2.0',
                 'paramiko>=2.7.1,<3.0.0',
                 'pyrecorder>=0.1.8,<0.2.0']}

entry_points = \
{'console_scripts': ['summit-tests = summit:run_tests']}

setup_kwargs = {
    'name': 'summit',
    'version': '0.8.6',
    'description': 'Tools for optimizing chemical processes',
    'long_description': '# Summit\n![summit_banner](https://raw.githubusercontent.com/sustainable-processes/summit/master/docs/source/_static/banner_4.png)\n\n<p align="center">\n<a href=\'https://gosummit.readthedocs.io/en/latest/?badge=latest\'>\n    <img src=\'https://readthedocs.org/projects/gosummit/badge/?version=latest\' alt=\'Documentation Status\' />\n</a>\n<a href="https://pypi.org/project/summit/"><img alt="PyPI" src="https://img.shields.io/pypi/v/summit"></a>\n</p>\n\nSummit is a set of tools for optimising chemical processes. We’ve started by targeting reactions. Go through a tutorial [here](https://colab.research.google.com/drive/1E_KVm-aZMqMm3memvesn3FIzGiXKHwJz#scrollTo=Wxg4TiHLV0Kd&uniqifier=2)!\n\n\n## What is Summit?\nCurrently, reaction optimisation in the fine chemicals industry is done by intuition or design of experiments.  Both scale poorly with the complexity of the problem. \n\nSummit uses recent advances in machine learning to make the process of reaction optimisation faster. Essentially, it applies algorithms that learn which conditions (e.g., temperature, stoichiometry, etc.) are important to maximising one or more objectives (e.g., yield, enantiomeric excess). This is achieved through an iterative cycle.\n\nSummit has two key features:\n\n- **Strategies**: Optimisation algorithms designed to find the best conditions with the least number of iterations. Summit has eight strategies implemented.\n- **Benchmarks**: Simulations of chemical reactions that can be used to test strategies. We have both mechanistic and data-driven benchmarks.\n\nTo get started, see the Quick Start below or follow our [tutorial](https://gosummit.readthedocs.io/en/latest/tutorial.html). \n\n## Installation\n\nTo install summit, use the following command:\n\n```pip install summit```\n\n## News\n\n* Denali (0.8) is out! Read more about the release [here](https://github.com/sustainable-processes/summit/releases/tag/0.8.0).\n* Kobi ([@marcosfelt](https://github.com/marcosfelt)) gave a tutorial on Summit at the online Autonomous Discovery Symposium on Wednesday 21 April 2021. The tutorial can be found [here](https://colab.research.google.com/drive/1E_KVm-aZMqMm3memvesn3FIzGiXKHwJz#scrollTo=Wxg4TiHLV0Kd&uniqifier=2).\n\n## Quick Start\n\nBelow, we show how to use the Nelder-Mead  strategy to optimise a benchmark representing a nucleophlic aromatic substitution (SnAr) reaction.\n\n```python\n# Import summit\nfrom summit.benchmarks import SnarBenchmark\nfrom summit.strategies import NelderMead, MultitoSingleObjective\nfrom summit.run import Runner\n\n# Instantiate the benchmark\nexp = SnarBenchmark()\n\n# Since the Snar benchmark has two objectives and Nelder-Mead is single objective, we need a multi-to-single objective transform\ntransform = MultitoSingleObjective(\n    exp.domain, expression="-sty/1e4+e_factor/100", maximize=False\n)\n\n# Set up the strategy, passing in the optimisation domain and transform\nnm = NelderMead(exp.domain, transform=transform)\n\n# Use the runner to run closed loop experiments\nr = Runner(\n    strategy=nm, experiment=exp,max_iterations=50\n)\nr.run()\n```\n\n## Documentation\n\nThe documentation for summit can be found [here](https://gosummit.readthedocs.io/en/latest/index.html).\n\n\n## Issues?\nSubmit an [issue](https://github.com/sustainable-processes/summit/issues) or send an email to kcmf2@cam.ac.uk.\n\n## Citing\n\nIf you find this project useful, we encourage you to\n\n* Star this repository :star: \n* Cite our [paper](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/cmtd.202000051).\n```\n@article{Felton2021,\nauthor = "Kobi Felton and Jan Rittig and Alexei Lapkin",\ntitle = "{Summit: Benchmarking Machine Learning Methods for Reaction Optimisation}",\nyear = "2021",\nmonth = "2",\nurl = "https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/cmtd.202000051",\njournal = "Chemistry Methods"\n}\n```\n\n',
    'author': 'Kobi Felton',
    'author_email': 'kobi.c.f@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sustainable-processes/summit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
