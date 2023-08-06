# Amplify

## Getting started
*Amplify* can be installed via `pip install amplify-model`. Then, the model can be used in an existing project by calling `from amplify.src.flex_calculation import FlexCalculator`.

Alternatively, the repo can of course be cloned. The source code of *Amplify* lies under ```amplify/src/flex_calculation.py```. Its results require the ```data_classes.py``` file. The calculation relies only on basic python modules.

## Tests
The basic tests lie under ```amplify/tests/unit_tests```. They can be started by calling ```pytest```.
- ```test_total_flex_calculation.py```: Assert valid flexibility calculation
- ```test_ppr_detection.py```: Validate problem detection
- ```test_accept_short_trades_scenarios.py```: Verify valid sizing of multi purpose obligations with MPOs lasting single time intervals
- ```test_accept_long_trades_scenarios.py```: Verify valid sizing of multi purpose obligations with MPOs lasting more than one time interval (contains multiple scenarios)
---
- ```full_result_test_accept_long_trades_scenarios.txt```: Contains result of full accept long trades test. For all failed tests, some information is given as well as a short summary.

## Requirements
Until now, *Amplify* only requires the ```pytest``` module, which can be installed via ```pip```.

## License
Amplify is licensed under the Apache 2.0 license.

## Project status
*Amplify* is still under development.

## Author of documentation
Paul Hendrik Tiemann (2022)
