from copy import deepcopy
from amplify.src.flex_calculation import *

FLEX_CALC_PARAMS = ['max_p_bat', 'min_p_bat', 'capacity_energy',
                    'efficiency_charge', 'efficiency_discharge',
                    'soh', 'problem_detection_horizon']

DEFAULT_PARAMETERS = {
    'max_p_bat': 250,
    'min_p_bat': -250,
    'capacity_energy': 250,
    'efficiency_charge': 0.9,
    'efficiency_discharge': 0.9,
    'soh': 1,
    'problem_detection_horizon': 8 * 15 * 60,
    'curr_soc': 0.7,
    'passed_time_of_curr_interval': 0,
    'avg_p_bat_of_curr_interval': 0,
    'mpos': [0, -108.0, -224.0, 0.0, -112.0, -6.0, -250, 0],
    'final_min_soc': 0,
    'final_max_soc': 1,
    'forecast': [1800, 2100, 2200, 2000, 2100, 1700, 2000, 2100],
    'p_max_ps': [2000] * 8,
    't_start': 100,
    'res': 15 * 60
}

parameter_set = deepcopy(DEFAULT_PARAMETERS)

# get params for flex calculator and create it
flex_calculator_params = {}
for k in FLEX_CALC_PARAMS:
    if k in parameter_set.keys():
        flex_calculator_params[k] = parameter_set[k]
        parameter_set.pop(k)

flex_calculator = FlexCalculator(**flex_calculator_params)

mpos = DEFAULT_PARAMETERS['mpos']
flex: FlexibilityCalculation = flex_calculator.calculate_total_flex(**parameter_set)
print(flex)
