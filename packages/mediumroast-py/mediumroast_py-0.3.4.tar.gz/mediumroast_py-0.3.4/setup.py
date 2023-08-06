# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mediumroast_py',
 'mediumroast_py.api',
 'mediumroast_py.extractors',
 'mediumroast_py.transformers']

package_data = \
{'': ['*']}

install_requires = \
['PyDocX>=0.9.10,<0.10.0',
 'boto3>=1.24.24,<2.0.0',
 'geopy>=2.2.0,<3.0.0',
 'pdfx>=1.4.1,<2.0.0',
 'pyfiglet>=0.8.post1,<0.9',
 'python-magic>=0.4.27,<0.5.0',
 'python-pptx>=0.6.21,<0.7.0',
 'requests>=2.28.1,<3.0.0',
 'spacy>=3.3.1,<4.0.0']

setup_kwargs = {
    'name': 'mediumroast-py',
    'version': '0.3.4',
    'description': 'A package to perform ETL (Extract, Transform and Load) and generally interact with the mediumroast.io application.',
    'long_description': "# Introduction\nThis is the Python Software Development Kit (SDK) for the mediumroast.io.  Internal tooling from Mediumroast, Inc. uses this SDK, so it will always be a first class citizen. Specifically, we build tools requiring ETL (Extract, Transform and Load), Machine Learning and Natural Language Processing (NLP) with this SDK. As appropriate examples illustrating various capabilities of the SDK can be found in the `examples/` directory of this package.  \n\n# Installation and Configuration Steps for Developers\nThe following steps are important if you are developing or extending the Python SDK.  If you're not a developer these steps aren't as important to you and you should pay attention to section entitled *Installation for Early Adopters and Testers*.\n\n## Cloning the repository for Developers\nAssuming `git` is installed and your credentials are set up to talk to the mediumroast.io set of repositories it should be possible to do the following as a user on the system:\n1. `mkdir ~/dev;cd ~/dev`\n2. `git clone git@github.com:mediumroast/mediumroast_py.git`\nThis will create an `mediumroast_py` directory in `~/dev/` and allow you to proceed to the following steps for installation.\n\n## Installation\nFor developers of the package the `setup.py` file is available to enable a local software distribution that can be improved upon.  As inspired by [this article](https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html) the best current way to perform the installation of a developer version after cloning is to assuming you've cloned into `~/dev`:\n1. `cd ~/dev/mr_sdk/python`\n2. `sudo pip install -e ./`\nWith this accomplished tools that you've written which depend upon this package should operate.  If there are issues encountered then please open an [issue](https://github.com/mediumroast/mr_python/issues).\n\n## Structure of the repository\nThe following structure is available for the Python SDK, as new SDK implementations are created additional top level directories will be created.\n```\nmr_python/\n      examples/\n      mediumroast_py/\n            api/\n            extractors/\n            transformers/\n            helpers.py\n      project.toml\n      README.md\n      LICENSE\n```\n\n# The Examples\nTo illustrate how to interact programmatically with the mediumroast.io application several examples have been created to make it easier for developers to interact with the system.  The scope of the examples, over time, will include all aspects of the SDK to speed up 3rd party development processes.  This means that over time examples for all apsects of the SDK will be produced and made available under the Apache Software License.  As with anything in the SDK if you run into problems please make sure that you raise an [issue](https://github.com/mediumroast/mediumroast_py/issues) in the repository.  More detail on the examples can be found within the [examples directory](https://github.com/mediumroast/mediumroast_py/tree/main/examples) of this repository.",
    'author': 'Michael Hay',
    'author_email': 'michael.hay@mediumroast.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mediumroast/mediumroast_py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
