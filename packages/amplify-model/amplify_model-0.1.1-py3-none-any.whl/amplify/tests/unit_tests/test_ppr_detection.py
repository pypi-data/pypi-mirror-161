import pytest
from copy import deepcopy
from typing import List, Dict, Tuple
from amplify.src.flex_calculation import FlexCalculator
from amplify.src.data_classes import Problem, FlexibilityCalculation, Flexibility


def create_problem_list(*prob_tuples) -> List[Problem]:
    prb_list: List[Problem] = []
    for problem_type, required, realizable, interval_no, negotiation_required  in prob_tuples:
        prb_list.append(Problem(problem_type=problem_type, required=required, realizable=realizable,
                                interval_no=interval_no, negotiation_required=negotiation_required))
    return prb_list



FLEX_CALC_PARAMS = ['max_p_bat', 'min_p_bat', 'capacity_energy', 'efficiency_charge', 'efficiency_discharge',
                 'soh', 'problem_detection_horizon']

DEFAULT_PARAMETERS = {
    'max_p_bat': 100,
    'min_p_bat': -100,
    'capacity_energy': 100,
    'efficiency_charge': 1,
    'efficiency_discharge': 1,
    'soh': 1,
    'problem_detection_horizon': 16 * 15 * 60,
    'curr_soc': 0.5,
    'passed_time_of_curr_interval': 0,
    'avg_p_bat_of_curr_interval': 0,
    'mpos': [0] * 16,
    'final_min_soc': 0,
    'final_max_soc': 1,
    'forecast': [1000] * 16,
    'p_max_ps': [1000] * 16,
    't_start': 100,
    'res': 15 * 60
}

testdata = {
    'plain': ({}, []),
    'P1_1 only 4': (
        {'forecast': [(4, 1110)]}, create_problem_list(('P1.1', -110, -100, 4, False))
    ),
    'P1_1 at 4 intervals': (
        {'forecast': [(0, 1140), (3, 1120), (6, 1200), (15, 2410)], 'curr_soc': 1},
        create_problem_list(
            ('P1.1', -140, -100, 0, False), ('P1.1', -120, -100, 3, False), ('P1.1', -200, -100, 6, False),
            ('P1.1', -1410, -100, 15, False))
    ),

    'P2_1 only 5': (
        {'forecast': [(5, 1080)], 'curr_soc': 0}, create_problem_list(
            ('P2.1', int((-80 * 0.25 / 100) * 1000), 0, 5, False))
    ),
    'P2_1 many intervals': (
        {'forecast': [(0, 1050), (3, 1050), (6, 1050), (14, 1050)], 'curr_soc': 0.2}, create_problem_list(
            ('P2.1', int((-200 * 0.25 / 100 + 0.2) * 1000), 0, 14, False)
        )
    ),

    'P1_1 -P2_1 mix': (
        {'forecast': [(0, 1150), (3, 1050), (6, 1050), (14, 1050)], 'curr_soc': 0.2}, create_problem_list(
            ('P1.1', -150, -100, 0, False),
            ('P2.1', int((-250 * 0.25 / 100 + 0.2) * 1000), 0, 14, False)
        )
    ),

    'P1_2 negative': (
        {'mpos': [(5, -120)], 'forecast': [(5, 500)]}, create_problem_list(('P1.2', -120, -100, 5, True))
    ),
    'P1_2 positive': (
        {'mpos': [(5, 120)], 'forecast': [(5, 500)]}, create_problem_list(('P1.2', 120, 100, 5, True))
    ),
    'P1_2 only 5': (
        {'mpos': [(5, 80)], 'forecast': [(5, 950)]}, create_problem_list(('P1.2', 80, 50, 5, True))
    ),
    'P1_2 many intervals': (
        {'mpos': [(5, 80), (3, 10), (9, 100), (2, 40), ]},
        create_problem_list(('P1.2', 80, 0, 5, True), ('P1.2', 10, 0, 3, True), ('P1.2', 100, 0, 9, True),
                            ('P1.2', 40, 0, 2, True),),
    ),

    'P2_2 only trade problem':(
        {'mpos': [(5, -50)], 'curr_soc': 0}, create_problem_list(
            ('P2.2', -50, 0, 5, True))
    ),

    'P2_2 trade problem with ps': (
        {'forecast': [(6, 1010)], 'mpos': [(5, -80)], 'curr_soc': 0.1}, create_problem_list(
            ('P2.2', -80, 0, 5, True))
    ),
    'P2_2 trade problem with ps and bilanzieller Flex': (
        {'forecast': [(5, 1020), (6, 1010)], 'mpos': [(5, -80)], 'curr_soc': 0.1}, create_problem_list(
            ('P2.2', -80, -20, 5, True))
    ),
    'P2_2 trade problem with ps and bilanzieller Flex and one ok trade': (
        {'forecast': [(5, 1020), (6, 1010)], 'mpos': [(4, -10), (5, -80)], 'curr_soc': 0.1}, create_problem_list(
            ('P2.2', -80, -20, 5, True))
    ),
    'P2_2 trade problem with ps and bilanzieller Flex and another trade': (
        {'forecast': [(4, 1010), (5, 1020), (6, 1010)], 'mpos': [(4, -20), (5, -80)], 'curr_soc': 0.1},
        create_problem_list(('P2.2', -80, -20, 5, True), ('P2.2', -20, -10, 4, True))
    ),

    'P2_2 trade problem with ps and bilanzieller Flex an unprob trade': (
        {'forecast': [(4, 1010), (5, 1020), (6, 1010)], 'mpos': [(4, -20), (5, -80)], 'curr_soc': 0.2},
        create_problem_list(('P2.2', -80, -20, 5, True))
    ),

    'P2_3 single trade': (
        {'forecast': [(0, 900), (5, 1020), (6, 1010)], 'mpos': [(0, 50), (5, -80)], 'curr_soc': 0.9},
        create_problem_list(('P2.3', 50, 0, 0, True))
    ),

    'P2_3 many trades': (
        {'forecast': [(0, 900), (1, 900), (2, 900)], 'mpos': [(0, 20), (1, 40), (2, 80)], 'curr_soc': 0.9},
        create_problem_list(('P2.3', 40, 0, 1, True), ('P2.3', 80, 0, 2, True))
    ),
}


@pytest.mark.parametrize(
    'adopted_params,expected_problems', testdata.values(), ids=testdata.keys()
)
def test_ppr(adopted_params: Dict, expected_problems: List[Problem]):
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

    flex = flex_calculator.calculate_total_flex(
        **parameter_set)

    problems: List[Problem] = flex.problems
    assert sorted(flex.problems, key=lambda x: (x.interval_no, x.problem_type)) == \
           sorted(expected_problems, key=lambda x: (x.interval_no, x.problem_type)), \
            f'parameters: {parameter_set}\nflex: {flex}\nproblems: {problems}\nexpected: {expected_problems}'
