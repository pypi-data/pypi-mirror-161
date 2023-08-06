import pytest

from amplify.src.flex_calculation import *

NUMBER_OF_TESTS_TO_RUN = 1000000
START_TEST_NO = 1

# parameters for testing:
MAX_P_BAT = [100, 75, 50]
MIN_P_BAT = [-100, -75, -50]
CAPACITY = [200, 100, 50]
START_SOC = [0, 0.25, 0.5, 0.75, 1]
EFF_CHARGE = [1, 0.9, 0.8]
EFF_DISCHARGE = [1, 0.9, 0.8]
PASSED_TIME_AVG_P_BAT = [(0, 0), (60, 0), (450, 40), (600, -50)]
MPOS = [
    [0, 0, 0, 0, 0, 0, 0, 0, ],
    [0, 0, 70, 0, 0, 0, 0, 0, ],
    [0, 0, 0, 0, 0, 0, -50, 0, ],
    [20, -10, 30, 40, -10, 0, 50, -50, ]
]
FINAL_MIN_MAX_SOC = [(0, 1), (0.25, 1), (0.3, 0.7)]
FORECAST = [
    [1000, 1100, 1150, 1150, 900, 850, 1000, 1100],
    [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
    [900, 900, 900, 800, 1100, 1050, 1000, 1150],
    [1100, 1200, 1250, 1000, 900, 800, 850, 850]
]
P_MAX = [
    [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
    [1100, 1100, 1100, 1100, 1100, 1100, 1100, 1100],
    [1000, 1000, 1000, 1000, 9000, 9000, 9000, 9000],
    [9000, 9000, 9000, 9000, 1000, 1000, 1000, 1000]
]

MAX_TEST_NO = len(MAX_P_BAT) * len(MIN_P_BAT) * len(CAPACITY) * len(START_SOC) * len(EFF_CHARGE) * len(EFF_DISCHARGE) \
              * len(PASSED_TIME_AVG_P_BAT) * len(MPOS) * len(FINAL_MIN_MAX_SOC) * len(FORECAST) * len(P_MAX)


def get_parameters(sim_no: int, as_str=False):
    # choose parameter set based on simulation number
    parameter_list = []
    for param in [MAX_P_BAT, MIN_P_BAT, CAPACITY, START_SOC, EFF_CHARGE, EFF_DISCHARGE, PASSED_TIME_AVG_P_BAT,
                  MPOS, FINAL_MIN_MAX_SOC, FORECAST, P_MAX]:
        # modulo operation helps to pass through all parameters
        parameter_list.append(param[sim_no % len(param)])
        sim_no //= len(param)
    if not as_str:
        return parameter_list
    else:
        return f'Forecast: {parameter_list[9]}\n P_Max: {parameter_list[10]} \n' \
               f'max_p_bat: {parameter_list[0]}, min_p_bat: {parameter_list[1]}, capacity: {parameter_list[2]}, ' \
               f'start_soc: {parameter_list[3]}\n' \
               f'mpos: {parameter_list[7]} \n final_min_max_soc: {parameter_list[8]}, ' \
               f'eff_charge: {parameter_list[4]}, ' \
               f'eff_discharge: {parameter_list[5]}, passed_time_avg_p_bat: {parameter_list[6]}'


@pytest.mark.parametrize(
    "sim_no", range(START_TEST_NO, min(START_TEST_NO + NUMBER_OF_TESTS_TO_RUN, MAX_TEST_NO))
)
def test_flex_calc(sim_no):
    max_p_bat, min_p_bat, capacity, start_soc, eff_charge, eff_discharge, (passed_time, avg_p_bat), mpos, \
        (final_min_soc, final_max_soc), forecast, p_max = get_parameters(sim_no)

    flex_calculator: FlexCalculator = FlexCalculator(max_p_bat=max_p_bat, min_p_bat=min_p_bat, capacity_energy=capacity,
                                                     efficiency_charge=eff_charge, efficiency_discharge=eff_discharge)

    flex: FlexibilityCalculation = \
        flex_calculator.calculate_total_flex(curr_soc=start_soc, passed_time_of_curr_interval=passed_time,
                                             avg_p_bat_of_curr_interval=avg_p_bat,
                                             mpos=mpos, final_min_soc=final_min_soc,
                                             final_max_soc=final_max_soc, forecast=forecast, p_max_ps=p_max,
                                             t_start=0)

    failing_str = f'{get_parameters(sim_no, True)}\n' \
                  f'Allowed p: ' \
                  f'{list(zip(flex.flex_with_mpo.allowed_min_power, flex.flex_with_mpo.allowed_max_power))}\n' \
                  f'Allowed soc: ' \
                  f'{list(zip(flex.flex_with_mpo.allowed_min_soc, flex.flex_with_mpo.allowed_max_soc))}\n' \
                  f'Problems: {flex.problems}'

    assert 1 >= min(flex.flex_with_mpo.allowed_max_soc) >= min(flex.flex_with_mpo.allowed_min_soc) >= 0, failing_str
    assert 1 >= max(flex.flex_without_mpo.allowed_max_soc) >= max(flex.flex_without_mpo.allowed_min_soc) >= 0, \
        failing_str

    if final_max_soc < flex.flex_with_mpo.allowed_max_soc[-1]:
        assert final_max_soc < flex.flex_with_mpo.allowed_min_soc[-1]
        # check if discharging was tried as much as possible
        for i in range(len(forecast) - 1, 0, -1):
            if flex.flex_with_mpo.allowed_max_soc[i] == 0:
                break
            assert flex.flex_with_mpo.allowed_min_power[i] == flex.flex_with_mpo.allowed_max_power[i], failing_str

    if final_min_soc > flex.flex_with_mpo.allowed_min_soc[-1]:
        assert final_min_soc > flex.flex_with_mpo.allowed_max_soc[-1]
        # check if charging was tried as much as possible
        for i in range(len(forecast) - 1, 0, -1):
            if flex.flex_with_mpo.allowed_max_soc[i] == 1:
                break
            assert flex.flex_with_mpo.allowed_min_power[i] == flex.flex_with_mpo.allowed_max_power[i], failing_str

    assert max_p_bat >= max(flex.flex_with_mpo.allowed_max_power) >= max(flex.flex_with_mpo.allowed_min_power), \
        failing_str
    assert min_p_bat <= min(flex.flex_with_mpo.allowed_min_power) <= min(flex.flex_with_mpo.allowed_max_power), \
        failing_str

    # read problem interval number
    peak_load_problem_intervals = [p.interval_no for p in flex.problems if p.problem_type == 'P1.1']
    trade_problem_intervals = [p.interval_no for p in flex.problems if p.problem_type in
                               ['P1.2', 'P1.3']]
    too_little_energy_for_trade = False
    too_much_energy_for_trade = False
    for p in flex.problems:
        if p.problem_type == 'P2.2':
            too_little_energy_for_trade = True
        if p.problem_type == 'P2.3':
            too_much_energy_for_trade = True
    energy_problem_detected = False
    for p in flex.problems:
        if p.problem_type == 'P2.1':
            energy_problem_detected = True

    for i, (allowed_max_p, allowed_min_p, forecast, this_p_max, mpo) in \
            enumerate(zip(flex.flex_with_mpo.allowed_max_power, flex.flex_with_mpo.allowed_min_power,
                          forecast, p_max, mpos)):
        assert allowed_max_p >= allowed_min_p
        # peak shaving fulfilled or Problem reported?
        assert allowed_max_p + forecast <= this_p_max or i in peak_load_problem_intervals \
               or energy_problem_detected, failing_str

        # MPO fulfilled?
        if mpo < 0:
            assert allowed_max_p <= mpo or i in trade_problem_intervals or energy_problem_detected \
                   or too_little_energy_for_trade, f'{get_parameters(sim_no, True)}\n' \
                                                   f'Allowed max p: {flex.flex_with_mpo.allowed_max_power}\n' \
                                                   f'Problems: {flex.problems}'
        if mpo > 0:
            assert allowed_min_p >= mpo or i in trade_problem_intervals or too_much_energy_for_trade, \
                f'{get_parameters(sim_no, True)}\nAllowed max p: {flex.flex_with_mpo.allowed_max_power}\n' \
                f'Problems: {flex.problems}'
