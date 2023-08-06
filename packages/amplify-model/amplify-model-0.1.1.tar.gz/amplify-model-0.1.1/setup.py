# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['amplify',
 'amplify.src',
 'amplify.tests',
 'amplify.tests.unit_tests',
 'amplify.tests.unit_tests.util']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=7.1.2,<8.0.0']

setup_kwargs = {
    'name': 'amplify-model',
    'version': '0.1.1',
    'description': 'Amplify (abstract multi-purpose-limited flexibility) is a model for operational flexibility remaining after a primary application is fullfilled by distributed energy resources.',
    'long_description': '# Amplify\n\n## Getting started\n*Amplify* can be installed via `pip install amplify-model`. Then, the model can be used in an existing project by calling `from amplify.src.flex_calculation import FlexCalculator`.\n\nAlternatively, the repo can of course be cloned. The source code of *Amplify* lies under ```amplify/src/flex_calculation.py```. Its results require the ```data_classes.py``` file. The calculation relies only on basic python modules.\n\n## Tests\nThe basic tests lie under ```amplify/tests/unit_tests```. They can be started by calling ```pytest```.\n- ```test_total_flex_calculation.py```: Assert valid flexibility calculation\n- ```test_ppr_detection.py```: Validate problem detection\n- ```test_accept_short_trades_scenarios.py```: Verify valid sizing of multi purpose obligations with MPOs lasting single time intervals\n- ```test_accept_long_trades_scenarios.py```: Verify valid sizing of multi purpose obligations with MPOs lasting more than one time interval (contains multiple scenarios)\n---\n- ```full_result_test_accept_long_trades_scenarios.txt```: Contains result of full accept long trades test. For all failed tests, some information is given as well as a short summary.\n\n## Requirements\nUntil now, *Amplify* only requires the ```pytest``` module, which can be installed via ```pip```.\n\n## License\nAmplify is licensed under the Apache 2.0 license.\n\n## Project status\n*Amplify* is still under development.\n\n## Author of documentation\nPaul Hendrik Tiemann (2022)\n',
    'author': 'Paul Hendrik Tiemann',
    'author_email': 'paul.hendrik.tiemann@uni-oldenburg.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
