import pytest
from copy import deepcopy
from amplify.src.flex_calculation import *
from amplify.tests.unit_tests.util.generate_trades import *
from amplify.tests.unit_tests.util.place_mpos import *

FLEX_CALC_PARAMS = ['max_p_bat', 'min_p_bat', 'capacity_energy', 'efficiency_charge', 'efficiency_discharge',
                 'soh', 'problem_detection_horizon']

DEFAULT_PARAMETERS = {
    'max_p_bat': 100,
    'min_p_bat': -100,
    'capacity_energy': 100,
    'efficiency_charge': 0.8,
    'efficiency_discharge': 0.9,
    'soh': 1,
    'problem_detection_horizon': 16 * 15 * 60,
    'curr_soc': 0.55,
    'passed_time_of_curr_interval': 180,
    'avg_p_bat_of_curr_interval': 0,
    'mpos': [0] * 8,
    'final_min_soc': 0,
    'final_max_soc': 1,
    'forecast': [900, 1050, 1100, 1000, 1050, 850, 1000, 1100],
    'p_max_ps': [1000] * 8,
    't_start': 100,
    'res': 15 * 60
}


testdata = {
    'default': ({}),
    'capacity200': ({'capacity_energy': 200,}),
}


@pytest.mark.parametrize(
    "adopted_params", testdata.values(), ids=testdata.keys()
)
def test_accept_short_trades(adopted_params):
    parameter_set = deepcopy(DEFAULT_PARAMETERS)

    for k, v in adopted_params.items():
        if k == 'forecast':
            for interval, new_p in v:
                # forecast adoptions are displayed differently
                parameter_set['forecast'][interval] = new_p
        elif k == 'mpos':
            for interval, new_p in v:
                # forecast adoptions are displayed differently
                parameter_set['mpos'][interval] = new_p
        else:
            parameter_set[k] = v

    # get params for flex calculator and create it
    flex_calculator_params = {}
    for k in FLEX_CALC_PARAMS:
        if k in parameter_set.keys():
            flex_calculator_params[k] = parameter_set[k]
            parameter_set.pop(k)

    flex_calculator = FlexCalculator(**flex_calculator_params)
    mpos_before_trades = parameter_set['mpos']

    flex_before_trades: FlexibilityCalculation = \
        flex_calculator.calculate_total_flex(**parameter_set)

    for startinterval_no in range(len(flex_before_trades.flex_with_mpo.allowed_min_power)):
    # place short power trades
        # charge trades
        if flex_before_trades.flex_with_mpo.allowed_max_power[startinterval_no] > 0:
            mpos_with_trades = generate_short_charge_trade(flex=flex_before_trades, mpos=mpos_before_trades, \
                startinterval_no=startinterval_no)

            assert_mpo_placement_valid(flex_calculator=flex_calculator, parameter_set=parameter_set,
                        mpos_with_trades=mpos_with_trades)


        # discharge trades
        if flex_before_trades.flex_with_mpo.allowed_min_power[startinterval_no] < 0:
            mpos_with_trades = generate_short_discharge_trade(flex=flex_before_trades, mpos=mpos_before_trades, \
                startinterval_no=startinterval_no)

            assert_mpo_placement_valid(flex_calculator=flex_calculator, parameter_set=parameter_set,
                        mpos_with_trades=mpos_with_trades,)

def assert_mpo_placement_valid(flex_calculator, parameter_set, mpos_with_trades):
    new_parameter_set = deepcopy(parameter_set)
    new_parameter_set['mpos'] = mpos_with_trades
    flex_with_trades: FlexibilityCalculation = \
        flex_calculator.calculate_total_flex(**new_parameter_set)
    assert flex_with_trades.problems == []
