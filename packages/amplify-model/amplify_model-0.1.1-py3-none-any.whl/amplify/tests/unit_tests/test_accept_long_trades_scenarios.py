import pytest
from typing import Dict
from copy import deepcopy
from amplify.src.flex_calculation import *
from amplify.tests.unit_tests.util.generate_trades import *
from amplify.tests.unit_tests.util.place_mpos import *

from typing import List, NamedTuple

class MarketFlexibility (NamedTuple):
    allowed_max_energy_delta: List[float]
    allowed_min_energy_delta: List[float]
    allowed_max_power: List[int]
    allowed_min_power: List[int]

class MarketFlexibilityCalculation(NamedTuple):
    """
    This class simply holds all the relevant information of a flex calculation
    """
    flex_with_mpo: MarketFlexibility
    t_create: int
    t_start: int
    res: int
    problems: List[Problem]

FLEX_CALC_PARAMS = ['max_p_bat', 'min_p_bat', 'capacity_energy',
                    'efficiency_charge', 'efficiency_discharge',
                    'soh', 'problem_detection_horizon']

# full flex
DEFAULT_PARAMETERS = {
    'max_p_bat': 250,
    'min_p_bat': -250,
    'capacity_energy': 250,
    'efficiency_charge': 0.9,
    'efficiency_discharge': 0.9,
    'soh': 1,
    'problem_detection_horizon': 8 * 15 * 60,
    'curr_soc': 0.55,
    'passed_time_of_curr_interval': 0,
    'avg_p_bat_of_curr_interval': 0,
    'mpos': [0] * 8,
    'final_min_soc': 0,
    'final_max_soc': 1,
    'forecast': [0.0] * 8,
    'p_max_ps': [2000] * 8,
    't_start': 100,
    'res': 15 * 60
}

testdata = {
    'full flex': ({}),
    'full flex_eff1.0': ({'efficiency_charge': 1, 'efficiency_discharge': 1}),
    'full flex_eff0.75': ({'efficiency_charge': 0.75, 'efficiency_discharge': 0.75}),
    'full flex_eff0.5': ({'efficiency_charge': 0.5, 'efficiency_discharge': 0.5}),
    'full flex_eff0.2': ({'efficiency_charge': 0.2, 'efficiency_discharge': 0.2}),
    'full flex_eff0.9short': ({'efficiency_charge': 0.9, 'efficiency_discharge': 0.9,'passed_time_of_curr_interval': 600, 'avg_p_bat_of_curr_interval': 30,}),
    'full flex_eff0.75short': ({'efficiency_charge': 0.75, 'efficiency_discharge': 0.75,'passed_time_of_curr_interval': 600, 'avg_p_bat_of_curr_interval': 30,}),
    'full flex_eff0.5short': ({'efficiency_charge': 0.5, 'efficiency_discharge': 0.5,'passed_time_of_curr_interval': 600, 'avg_p_bat_of_curr_interval': 30,}),
    'full flex_eff0.2short': ({'efficiency_charge': 0.2, 'efficiency_discharge': 0.2,'passed_time_of_curr_interval': 600, 'avg_p_bat_of_curr_interval': 30,}),
}

# with PS and recharge
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
    'mpos': [0] * 8,
    'final_min_soc': 0,
    'final_max_soc': 1,
    'forecast': [1700, 2200, 2200, 2100, 1700, 1700, 2200, 1900],
    'p_max_ps': [2000] * 8,
    't_start': 100,
    'res': 15 * 60
}

# with PS without recharge
DEFAULT_PARAMETERS = {
    'max_p_bat': 250,
    'min_p_bat': -250,
    'capacity_energy': 250,
    'efficiency_charge': 0.9,
    'efficiency_discharge': 0.9,
    'soh': 1,
    'problem_detection_horizon': 8 * 15 * 60,
    'curr_soc': 0.9,
    'passed_time_of_curr_interval': 0,
    'avg_p_bat_of_curr_interval': 0,
    'mpos': [0] * 8,
    'final_min_soc': 0,
    'final_max_soc': 1,
    'forecast': [2040, 2200, 2200, 2100, 1900, 1700, 1600, 1900],
    'p_max_ps': [2000] * 8,
    't_start': 100,
    'res': 15 * 60
}

# with prior MPOs
DEFAULT_PARAMETERS = {
    'max_p_bat': 250,
    'min_p_bat': -250,
    'capacity_energy': 250,
    'efficiency_charge': 0.9,
    'efficiency_discharge': 0.9,
    'soh': 1,
    'problem_detection_horizon': 8 * 15 * 60,
    'curr_soc': 0.9,
    'passed_time_of_curr_interval': 0,
    'avg_p_bat_of_curr_interval': 0,
    'mpos': [40, -40, -40, 0, -40, 40, -40, -40],
    'final_min_soc': 0,
    'final_max_soc': 1,
    'forecast': [1840, 1800, 1800, 1900, 1900, 1700, 1600, 190],
    'p_max_ps': [2000] * 8,
    't_start': 100,
    'res': 15 * 60
}

# for PS and prior MPOs
testdata = {
    'default': ({}),
    'default_forecast': ({'forecast': [(0,1800), (1,2100), (2,2200), (3,2000), (4,2100), (5,1700), (6,2000), (7,2100)],}),
    'capacity200': ({'capacity_energy': 500,}),
    'current_interval_short': ({'passed_time_of_curr_interval': 180}),
    'current_interval_very_short': ({'passed_time_of_curr_interval': 600, 'avg_p_bat_of_curr_interval': 20,}),
    'current_interval_wrong': ({'passed_time_of_curr_interval': 180, 'avg_p_bat_of_curr_interval': -40,}),
    'low_efficiency': ({'efficiency_charge': 0.65, 'efficiency_discharge': 0.65,'final_min_soc': 0.5,}),
    'extremely_low_efficiency': ({'efficiency_charge': 0.2, 'efficiency_discharge': 0.2, 'curr_soc': 1, 'forecast': [(0,2000), (2,2040)],
                                  'forecast': [(0,1800), (1,2040), (2,2000), (3,2040), (4,2040), (5,1700), (6,2000), (7,2040)]}),
    'low_efficiency_with_curr_int': ({'efficiency_charge': 0.2, 'efficiency_discharge': 0.2, 'curr_soc': 1,
                                  'forecast': [(0,2020), (1,2040), (2,2020), (3,1800), (4,2040), (5,1700), (6,1600), (7,2040)],
                                  'passed_time_of_curr_interval': 300, 'avg_p_bat_of_curr_interval': 10,}),
}


def add_sim_no_to_testdata(testdata: dict, no_intervals=8):
    """

    :param testdata:
    :return:
    """
    new_testdata = {}
    for key, value in testdata.items():
        for i in range(no_intervals):
            new_testdata[f'{key}_{i}_fast_charge'] = (value, i, 'fast_charge')
            new_testdata[f'{key}_{i}_slow_charge'] = (value, i, 'slow_charge')
            new_testdata[f'{key}_{i}_fast_discharge'] = (value, i, 'fast_discharge')
            new_testdata[f'{key}_{i}_slow_discharge'] = (value, i, 'slow_discharge')
    return new_testdata


testdata = add_sim_no_to_testdata(testdata=testdata)


@pytest.mark.parametrize(
    "adopted_params,interval_no,mpo_type", testdata.values(), ids=testdata.keys()
)
def test_accept_long_trades(adopted_params: Dict, interval_no: int, mpo_type: str):
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
    flex_before_trades: FlexibilityCalculation = flex_calculator.calculate_total_flex(**parameter_set)
    marketflex_before_trades: MarketFlexibilityCalculation = calculate_market_flexibility(flex=flex_before_trades, mpos=mpos_before_trades)
    # Attention: pass_flexibility_to_visualization changes length of flexibility and mpo vectors
    # pass_flexibility_to_visualization(max_p_bat=max_p_bat, min_p_bat=min_p_bat, capacity_energy=capacity,
    #                                                  efficiency_charge=eff_charge, efficiency_discharge=eff_discharge,
    #                                                  curr_soc=start_soc, passed_time_of_curr_interval=passed_time,
    #                                                  avg_p_bat_of_curr_interval=avg_p_bat,
    #                                                  mpos=mpos_before_trades.copy(), final_min_soc=final_min_soc,
    #                                                  final_max_soc=final_max_soc, forecast=forecast, p_max_ps=p_max,
    #                                                  t_start=0)

    if marketflex_before_trades.problems == []: # tests with initial ppr should not fail for easier test implementation
    # place long charge trades
        # trades that use most available power and all energy from startinterval_no
        if mpo_type == 'fast_charge':
            mpos_with_trades = generate_long_fast_charge_trade(flex=marketflex_before_trades, mpos=parameter_set['mpos'], \
                startinterval_no=interval_no)
            assert_mpo_placement_valid(flex_calculator=flex_calculator, parameter_set=parameter_set,
                        mpos_with_trades=mpos_with_trades)

        # trades that use most available power and all energy before endinterval_no
        if mpo_type == 'slow_charge':
            mpos_with_trades = generate_long_slow_charge_trade(flex=marketflex_before_trades, mpos=mpos_before_trades, \
                endinterval_no=interval_no)
            assert_mpo_placement_valid(flex_calculator=flex_calculator, parameter_set=parameter_set,
                        mpos_with_trades=mpos_with_trades)

    # place long discharge trades
        # trades that use most available power and all energy from startinterval_no
        if mpo_type == 'fast_discharge':
            mpos_with_trades = generate_long_fast_discharge_trade(flex=marketflex_before_trades, mpos=mpos_before_trades, \
                startinterval_no=interval_no)
            assert_mpo_placement_valid(flex_calculator=flex_calculator, parameter_set=parameter_set,
                        mpos_with_trades=mpos_with_trades)

        # trades that use most available power and all energy before endinterval_no
        if mpo_type == 'slow_discharge':
            print(flex_before_trades)
            mpos_with_trades = generate_long_slow_discharge_trade(flex=marketflex_before_trades, mpos=mpos_before_trades, \
                endinterval_no=interval_no)
            assert_mpo_placement_valid(flex_calculator=flex_calculator, parameter_set=parameter_set,
                        mpos_with_trades=mpos_with_trades)
    else: # skip test
        pytest.skip("PPR in initial flex calculation")

def calculate_market_flexibility(flex, mpos):
    cumulated_mpos = 0
    allowed_max_power = []
    allowed_min_power = []
    allowed_max_energy_delta = []
    allowed_min_energy_delta = []

    for interval_no in range(len(flex.flex_with_mpo.allowed_max_power)):
        allowed_max_power.append(
            flex.flex_with_mpo.allowed_max_power[interval_no] -
            mpos[interval_no]
        )
        allowed_min_power.append(
            flex.flex_with_mpo.allowed_min_power[interval_no] -
            mpos[interval_no]
        )
        cumulated_mpos = cumulated_mpos + mpos[interval_no]

        allowed_max_energy_delta.append(
            flex.flex_with_mpo.allowed_max_energy_delta[interval_no] -
            cumulated_mpos * flex.res/3600
        )
        allowed_min_energy_delta.append(
            flex.flex_with_mpo.allowed_min_energy_delta[interval_no] -
            cumulated_mpos * flex.res/3600
        )

    flex_with_mpo = MarketFlexibility(
        allowed_max_energy_delta=allowed_max_energy_delta,
        allowed_min_energy_delta=allowed_min_energy_delta,
        allowed_max_power=allowed_max_power,
        allowed_min_power=allowed_min_power,
    )
    result = MarketFlexibilityCalculation(
        t_create=int(time.time()),
        t_start=flex.t_start,
        res=flex.res,
        flex_with_mpo=flex_with_mpo,
        problems=flex.problems
    )
    return result

def assert_mpo_placement_valid(flex_calculator, parameter_set, mpos_with_trades):
    new_parameter_set = deepcopy(parameter_set)
    for interval_no in range(len(mpos_with_trades)):
        if parameter_set['mpos'][interval_no] < 0 or parameter_set['mpos'][interval_no] > 0:
            if mpos_with_trades[interval_no] >= 0:
                assert parameter_set['mpos'][interval_no] >= 0, \
                    f'Positive MPO during time interval {interval_no} with originally negative or no MPO'
                assert mpos_with_trades[interval_no] >= parameter_set['mpos'][interval_no], \
                    f'Positive MPO during time interval {interval_no} smaller then original positive MPO'
            elif mpos_with_trades[interval_no] <= 0:
                assert parameter_set['mpos'][interval_no] <= 0, \
                    f'Negative MPO during time interval {interval_no} with originally positive or no MPO'
                assert mpos_with_trades[interval_no] <= parameter_set['mpos'][interval_no], \
                    f'Negative MPO during time interval {interval_no} smaller then original negative MPO'

    new_parameter_set['mpos'] = mpos_with_trades
    flex_with_trades: FlexibilityCalculation = \
        flex_calculator.calculate_total_flex(**new_parameter_set)
    assert flex_with_trades.problems == []
