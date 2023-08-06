from amplify.src.data_classes import FlexibilityCalculation, Flexibility, Problem


def aggregate_flexibility(flex1, flex2):
    # store result in named tuple
    result_no_mpo = Flexibility(
        available_min_power=None,
        available_max_power=None,
        required_min_soc=None,
        required_max_soc=None,
        reachable_min_soc=None,
        reachable_max_soc=None,
        allowed_min_soc=None,
        allowed_max_soc=None,
        allowed_max_energy_delta = [flex1.flex_without_mpo.allowed_max_energy_delta[int] + \
            flex2.flex_without_mpo.allowed_max_energy_delta[int] for int in range(len(flex1.flex_without_mpo.allowed_max_power))],
        allowed_min_energy_delta= [flex1.flex_without_mpo.allowed_min_energy_delta[int] + \
            flex2.flex_without_mpo.allowed_min_energy_delta[int] for int in range(len(flex1.flex_without_mpo.allowed_max_power))],
        allowed_max_power= [flex1.flex_without_mpo.allowed_max_power[int] + \
            flex2.flex_without_mpo.allowed_max_power[int] for int in range(len(flex1.flex_without_mpo.allowed_max_power))],
        allowed_min_power= [flex1.flex_without_mpo.allowed_min_power[int] + \
            flex2.flex_without_mpo.allowed_min_power[int] for int in range(len(flex1.flex_without_mpo.allowed_max_power))],
    )

    result_with_mpo = Flexibility(
        available_min_power=None,
        available_max_power=None,
        required_min_soc=None,
        required_max_soc=None,
        reachable_min_soc=None,
        reachable_max_soc=None,
        allowed_min_soc=None,
        allowed_max_soc=None,
        allowed_max_energy_delta = [flex1.flex_with_mpo.allowed_max_energy_delta[int] + \
            flex2.flex_with_mpo.allowed_max_energy_delta[int] for int in range(len(flex1.flex_with_mpo.allowed_max_power))],
        allowed_min_energy_delta= [flex1.flex_with_mpo.allowed_min_energy_delta[int] + \
            flex2.flex_with_mpo.allowed_min_energy_delta[int] for int in range(len(flex1.flex_with_mpo.allowed_max_power))],
        allowed_max_power= [flex1.flex_with_mpo.allowed_max_power[int] + \
            flex2.flex_with_mpo.allowed_max_power[int] for int in range(len(flex1.flex_with_mpo.allowed_max_power))],
        allowed_min_power= [flex1.flex_with_mpo.allowed_min_power[int] + \
            flex2.flex_with_mpo.allowed_min_power[int] for int in range(len(flex1.flex_with_mpo.allowed_max_power))],
    )

    result = FlexibilityCalculation(
        t_create=flex1.t_create,
        t_start=flex1.t_start,
        res=flex1.res,
        flex_with_mpo=result_with_mpo,
        flex_without_mpo=result_no_mpo,
        problems=flex1.problems.append(flex2.problems)
    )

    if result.problems is not None:
        print(f'Probleme: {result.problems}')

    return result

    # available_min_power=flex1.flex_without_mpo.available_min_power + \
    #     flex2.flex_without_mpo.available_min_power,
    # available_max_power=flex1.flex_without_mpo.available_max_power + \
    #     flex2.flex_without_mpo.available_max_power,
    # required_min_soc=flex1.flex_without_mpo.required_min_soc + \
    #     flex2.flex_without_mpo.required_min_soc,
    # required_max_soc=flex1.flex_without_mpo.required_max_soc + \
    #     flex2.flex_without_mpo.required_max_soc,
    # reachable_min_soc=flex1.flex_without_mpo.reachable_min_soc + \
    #     flex2.flex_without_mpo.required_min_soc,
    # reachable_max_soc=flex1.flex_without_mpo.reachable_max_soc + \
    #     flex2.flex_without_mpo.required_max_soc,
