# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clinicadl',
 'clinicadl.extract',
 'clinicadl.generate',
 'clinicadl.interpret',
 'clinicadl.predict',
 'clinicadl.quality_check',
 'clinicadl.quality_check.t1_linear',
 'clinicadl.quality_check.t1_volume',
 'clinicadl.random_search',
 'clinicadl.resources.masks',
 'clinicadl.resources.models',
 'clinicadl.train',
 'clinicadl.train.tasks',
 'clinicadl.tsvtools',
 'clinicadl.tsvtools.analysis',
 'clinicadl.tsvtools.getlabels',
 'clinicadl.tsvtools.kfold',
 'clinicadl.tsvtools.restrict',
 'clinicadl.tsvtools.split',
 'clinicadl.utils',
 'clinicadl.utils.caps_dataset',
 'clinicadl.utils.cli_param',
 'clinicadl.utils.maps_manager',
 'clinicadl.utils.meta_maps',
 'clinicadl.utils.network',
 'clinicadl.utils.network.autoencoder',
 'clinicadl.utils.network.cnn',
 'clinicadl.utils.network.vae',
 'clinicadl.utils.split_manager',
 'clinicadl.utils.task_manager']

package_data = \
{'': ['*'], 'clinicadl': ['resources/config/*']}

install_requires = \
['click-option-group>=0.5,<0.6',
 'click>=8,<9',
 'clinica>=0.7.0,<0.8.0',
 'numpy>=1.17,<2.0',
 'pandas>=1.2,<2.0',
 'pynvml',
 'scikit-image>=0.19,<0.20',
 'scikit-learn>=1.0,<2.0',
 'tensorboard',
 'toml',
 'torch>=1.8.0,<2.0.0',
 'torchvision']

extras_require = \
{'docs': ['mkdocs>=1.1,<2.0', 'mkdocs-material', 'pymdown-extensions']}

entry_points = \
{'console_scripts': ['clinicadl = clinicadl.cmdline:cli']}

setup_kwargs = {
    'name': 'clinicadl',
    'version': '1.1.1',
    'description': 'Framework for the reproducible processing of neuroimaging data with deep learning methods',
    'long_description': '<h1 align="center">\n  <a href="http://www.clinicadl.readthedocs.io">\n    <img src="https://clinicadl.readthedocs.io/en/latest/images/logo.png" alt="ClinicaDL Logo" width="120" height="120">\n  </a>\n  <br/>\n  ClinicaDL\n</h1>\n\n<p align="center"><strong>Framework for the reproducible processing of neuroimaging data with deep learning methods</strong></p>\n\n<p align="center">\n  <a href="https://ci.inria.fr/clinicadl/job/AD-DL/job/dev/">\n    <img src="https://ci.inria.fr/clinicadl/buildStatus/icon?job=AD-DL%2Fdev" alt="Build Status">\n  </a>\n  <a href="https://badge.fury.io/py/clinicadl">\n    <img src="https://badge.fury.io/py/clinicadl.svg" alt="PyPI version">\n  </a>\n  <a href=\'https://clinicadl.readthedocs.io/en/latest/?badge=latest\'>\n    <img src=\'https://readthedocs.org/projects/clinicadl/badge/?version=latest\' alt=\'Documentation Status\' />\n  </a>\n\n</p>\n\n<p align="center">\n  <a href="https://clinicadl.readthedocs.io/">Documentation</a> |\n  <a href="https://aramislab.paris.inria.fr/clinicadl/tuto">Tutorial</a> |\n  <a href="https://groups.google.com/forum/#!forum/clinica-user">Forum</a>\n</p>\n\n\n## About the project\n\nThis repository hosts ClinicaDL, the deep learning extension of [Clinica](https://github.com/aramis-lab/clinica), \na python library to process neuroimaging data in [BIDS](https://bids.neuroimaging.io/index.html) format.\n\n> **Disclaimer:** this software is **under development**. Some features can\nchange between different releases and/or commits.\n\nTo access the full documentation of the project, follow the link \n[https://clinicadl.readthedocs.io/](https://clinicadl.readthedocs.io/). \nIf you find a problem when using it or if you want to provide us feedback,\nplease [open an issue](https://github.com/aramis-lab/ad-dl/issues) or write on\nthe [forum](https://groups.google.com/forum/#!forum/clinica-user).\n\n## Getting started\nClinicaDL currently supports macOS and Linux.\n\nWe recommend to use `conda` or `virtualenv` for the installation of ClinicaDL\nas it guarantees the correct management of libraries depending on common\npackages:\n\n```{.sourceCode .bash}\nconda create --name ClinicaDL python=3.8\nconda activate ClinicaDL\npip install clinicadl\n```\n\n## Tutorial \nVisit our [hands-on tutorial web\nsite](https://aramislab.paris.inria.fr/clinicadl/tuto) to start\nusing **ClinicaDL** directly in a Google Colab instance!\n\n## Related Repositories\n\n- [Clinica: Software platform for clinical neuroimaging studies](https://github.com/aramis-lab/clinica)\n- [AD-DL: Convolutional neural networks for classification of Alzheimer\'s disease: Overview and reproducible evaluation](https://github.com/aramis-lab/AD-DL)\n- [AD-ML: Framework for the reproducible classification of Alzheimer\'s disease using machine learning](https://github.com/aramis-lab/AD-ML)\n\n## Citing us\n\n- Thibeau-Sutre, E., Díaz, M., Hassanaly, R., Routier, A., Dormont, D., Colliot, O., Burgos, N.: ‘ClinicaDL: an open-source deep learning software for reproducible neuroimaging processing‘, 2021. [hal-03351976](https://hal.inria.fr/hal-03351976)\n- Routier, A., Burgos, N., Díaz, M., Bacci, M., Bottani, S., El-Rifai O., Fontanella, S., Gori, P., Guillon, J., Guyot, A., Hassanaly, R., Jacquemont, T.,  Lu, P., Marcoux, A.,  Moreau, T., Samper-González, J., Teichmann, M., Thibeau-Sutre, E., Vaillant G., Wen, J., Wild, A., Habert, M.-O., Durrleman, S., and Colliot, O.: ‘Clinica: An Open Source Software Platform for Reproducible Clinical Neuroscience Studies’, 2021. [doi:10.3389/fninf.2021.689675](https://doi.org/10.3389/fninf.2021.689675) [Open Access version](https://hal.inria.fr/hal-02308126)\n',
    'author': 'ARAMIS Lab',
    'author_email': None,
    'maintainer': 'Clinica developers',
    'maintainer_email': 'clinica-user@inria.fr',
    'url': 'https://clinicadl.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
