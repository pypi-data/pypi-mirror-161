# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['btyd', 'btyd.datasets', 'btyd.fitters', 'btyd.models']

package_data = \
{'': ['*']}

install_requires = \
['autograd==1.4', 'dill==0.3.5.1', 'numpy>=1.20.0,<2.0.0', 'pymc>=4.0.0,<5.0.0']

setup_kwargs = {
    'name': 'btyd',
    'version': '0.1b1',
    'description': 'Buy Till You Die and Customer Lifetime Value statistical models in Python.',
    'long_description': '# BTYD\n\n[![Actively Maintained](https://img.shields.io/badge/Development%20Status-Active%20-yellowgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)\n[![PyPI version](https://badge.fury.io/py/btyd.svg)](https://badge.fury.io/py/btyd)\n[![GitHub license](https://img.shields.io/github/license/ColtAllen/btyd)](https://github.com/ColtAllen/btyd/blob/master/LICENSE.txt)\n\n\n## READ FIRST: Project Status\n\nBTYD is the successor to the [Lifetimes](https://github.com/CamDavidsonPilon/lifetimes) library for implementing Buy Till You Die and Customer Lifetime Value statistical models in Python. All existing Lifetimes functionality is supported, and Bayesian [PyMC](https://github.com/pymc-devs) model implementations are presently in Beta.\n\n\n## Introduction\n\nBTYD can be used to analyze your users based on the following assumptions:\n\n1. Users interact with you when they are active, or "alive"\n2. Users under study may "die" or become inactive after some period of time\n\nIf this is too abstract, consider these applications:\n\n - Predicting how often a visitor will return to your website. (Alive = visiting. Die = decided the website wasn\'t for them)\n - Understanding how frequently a patient may return to a hospital. (Alive = visiting. Die = maybe the patient moved to a new city, or became deceased.)\n - Predicting individuals who have churned from an app using only their usage history. (Alive = logins. Die = removed the app)\n - Predicting repeat purchases from a customer. (Alive = actively purchasing. Die = became disinterested with your product)\n - Predicting the lifetime value of your customers\n\n\n## Installation\n\n```bash\npip install btyd\n```\n\n## Contributing\n\nPlease refer to the [Contributing Guide](https://github.com/ColtAllen/btyd/blob/master/CONTRIBUTING.md) before creating any *Pull Requests*.\n\n## Documentation and Tutorials\n[User Guide](https://btyd.readthedocs.io/en/latest/User%20Guide.html)\n\n\n## Questions? Comments? Requests?\n\nPlease create an issue in the [BTYD repository](https://github.com/ColtAllen/btyd/issues).\n\n## Supported Models\n\n- **BG/NBD** Fader, Peter S., Bruce G.S. Hardie, and Ka Lok Lee (2005a),\n       ["Counting Your Customers the Easy Way: An Alternative to the\n       Pareto/NBD Model"](http://brucehardie.com/papers/018/fader_et_al_mksc_05.pdf), Marketing Science, 24 (2), 275-84.\n\n## Additional Information\n\n1. R implementation is called [BTYDplus](https://github.com/mplatzer/BTYDplus).\n1. [Bruce Hardie\'s website](http://brucehardie.com/), especially his notes, is full of useful and essential explanations, many of which are featured in this library.\n',
    'author': 'Colt Allen',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
