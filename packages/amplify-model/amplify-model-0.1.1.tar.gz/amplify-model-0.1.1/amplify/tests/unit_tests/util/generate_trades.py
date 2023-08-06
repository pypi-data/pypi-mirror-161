from amplify.src.flex_calculation import *

def generate_short_charge_trade(flex: FlexibilityCalculation, mpos, startinterval_no):
    """

    """
    mpos_with_trades = mpos.copy()
    mpos_with_trades[startinterval_no] = flex.flex_with_mpo.allowed_max_power[startinterval_no]
    return mpos_with_trades

def generate_short_discharge_trade(flex: FlexibilityCalculation, mpos, startinterval_no):
    """

    """
    mpos_with_trades = mpos.copy()
    mpos_with_trades[startinterval_no] = flex.flex_with_mpo.allowed_min_power[startinterval_no]
    return mpos_with_trades

def generate_long_fast_charge_trade(flex: FlexibilityCalculation, mpos, startinterval_no):
    """
    Generates a multi-time-step trade, which starts at startinterval_no and
    takes as much charge power as possible until the max energy level is reached
    """
    print(f'Start interval: {startinterval_no}\nFlexibility: {flex.flex_with_mpo}\nMPOs: {mpos}')
    charge_possible_until = len(flex.flex_with_mpo.allowed_min_power)
    duration = len(flex.flex_with_mpo.allowed_min_power) - startinterval_no
    for interval_no in range(startinterval_no, len(flex.flex_with_mpo.allowed_min_power)):
        print(f'{interval_no} ',end='')
        # verify charge is possible
        if flex.flex_with_mpo.allowed_max_power[interval_no] < 0:
            charge_possible_until = interval_no
            duration = charge_possible_until - startinterval_no
            break
    print(f'\nCharge possible until: {charge_possible_until}')
    # generate multi-time-step trade
    trade_power = [0.0]*len(flex.flex_with_mpo.allowed_max_power)
    trade_energy_delta = [0.0]*(len(trade_power))
    if startinterval_no > 0:
        trade_energy_delta[startinterval_no-1] = flex.flex_with_mpo.allowed_min_energy_delta[startinterval_no-1]

    for interval_no in range(startinterval_no, charge_possible_until):
        print(f'Initial energy level in {interval_no}: {trade_energy_delta[interval_no-1]}')
        power_this_interval = flex.flex_with_mpo.allowed_max_power[interval_no]
        print(f'One-step charge power in {interval_no}: {power_this_interval}')

        # increase min energy level by max power
        increased_min_energy_delta = power_this_interval * 900/3600 + trade_energy_delta[interval_no-1]
        print(f'Increased min energy level: {increased_min_energy_delta}, Max allowed energy delta: {flex.flex_with_mpo.allowed_max_energy_delta[interval_no]}')
        if increased_min_energy_delta > flex.flex_with_mpo.allowed_max_energy_delta[interval_no]:
            # limit trade power in case of energy limit
            power_this_interval = (flex.flex_with_mpo.allowed_max_energy_delta[interval_no] - trade_energy_delta[interval_no-1]) / 900*3600
            if power_this_interval < max(0,flex.flex_with_mpo.allowed_min_power[interval_no]):
                # interrupt if limited trade power not allowed
                duration = interval_no-1
                print(f'Break due to invalid power. Duration: {duration}')
                break

        # update trade_energy_delta
        trade_energy_delta[interval_no] = trade_energy_delta[interval_no-1] + power_this_interval*900/3600

        if trade_energy_delta[interval_no] < flex.flex_with_mpo.allowed_min_energy_delta[interval_no] or \
            trade_energy_delta[interval_no] > flex.flex_with_mpo.allowed_max_energy_delta[interval_no]:
            # end trade if energy level not valid
            duration = interval_no-1
            print(f'Break due to invalid energy. Duration: {duration}')
            break

        print(f'Current trade power in {interval_no}: {power_this_interval}')
        trade_power[interval_no] = power_this_interval
        assert trade_power[interval_no] >= 0, f'Trade power: {trade_power}'

    print(f'Final trade power: {trade_power}\nFinal start interval: {startinterval_no}, final duration: {duration}')
    mpos_with_trades = mpos.copy()
    for interval_no in range(startinterval_no, charge_possible_until):
        mpos_with_trades[interval_no] = mpos_with_trades[interval_no] + trade_power[interval_no]
        # mpos_with_trades[interval_no] = trade_power[interval_no]

    # validate_charge_trade(flex, mpos_with_trades, startinterval_no, duration)

    print(f'MPOs: {mpos_with_trades}')
    return mpos_with_trades

def generate_long_fast_discharge_trade(flex: FlexibilityCalculation, mpos, startinterval_no):
    """
    Generates a multi-time-step trade, which starts at startinterval_no and
    takes as much discharge power as possible until the min energy level is reached
    """
    print(f'Start interval: {startinterval_no}\nFlexibility: {flex.flex_with_mpo}\nMPOs: {mpos}')
    discharge_possible_until = len(flex.flex_with_mpo.allowed_min_power)
    duration = len(flex.flex_with_mpo.allowed_min_power) - startinterval_no
    for interval_no in range(startinterval_no, len(flex.flex_with_mpo.allowed_min_power)):
        print(f'{interval_no} ',end='')
        # verify discharge is possible
        if flex.flex_with_mpo.allowed_min_power[interval_no] > 0:
            discharge_possible_until = interval_no
            duration = discharge_possible_until - startinterval_no
            break
    print(f'\nDischarge possible until: {discharge_possible_until}')
    # generate multi-time-step trade
    trade_power = [0.0]*len(flex.flex_with_mpo.allowed_max_power)
    trade_energy_delta = [0.0]*(len(trade_power))
    if startinterval_no > 0:
        trade_energy_delta[startinterval_no-1] = flex.flex_with_mpo.allowed_max_energy_delta[startinterval_no-1]

    for interval_no in range(startinterval_no, discharge_possible_until):
        print(f'Initial energy level in {interval_no}: {trade_energy_delta[interval_no-1]}')
        power_this_interval = flex.flex_with_mpo.allowed_min_power[interval_no]
        print(f'One-step discharge power in {interval_no}: {power_this_interval}')

        # decrease max energy level by min power
        decreased_max_energy_delta = power_this_interval * 900/3600 + trade_energy_delta[interval_no-1]
        print(f'Decreased max energy level: {decreased_max_energy_delta}, Min allowed energy delta: {flex.flex_with_mpo.allowed_min_energy_delta[interval_no]}')
        if decreased_max_energy_delta < flex.flex_with_mpo.allowed_min_energy_delta[interval_no]:
            # limit trade power in case of energy limit
            power_this_interval = (flex.flex_with_mpo.allowed_min_energy_delta[interval_no] - trade_energy_delta[interval_no-1]) / 900*3600
            print(f'Limited trade power in {interval_no}: {power_this_interval}')
            if power_this_interval > min(0,flex.flex_with_mpo.allowed_max_power[interval_no]):
                # interrupt if limited trade power not allowed
                duration = interval_no-1
                print(f'Break due to invalid power. Duration: {duration}')
                break

        # update trade_energy_delta
        trade_energy_delta[interval_no] = trade_energy_delta[interval_no-1] + power_this_interval*900/3600

        if trade_energy_delta[interval_no] < flex.flex_with_mpo.allowed_min_energy_delta[interval_no] or \
            trade_energy_delta[interval_no] > flex.flex_with_mpo.allowed_max_energy_delta[interval_no]:
            # end trade if energy level not valid
            duration = interval_no-1
            print(f'Break due to invalid energy. Duration: {duration}')
            break

        print(f'Current trade power in {interval_no}: {power_this_interval}')
        trade_power[interval_no] = power_this_interval
        assert trade_power[interval_no] <= 0, f'Trade power: {trade_power}'

    print(f'Final trade power: {trade_power}\nFinal start interval: {startinterval_no}, final duration: {duration}')
    mpos_with_trades = mpos.copy()
    for interval_no in range(startinterval_no, discharge_possible_until):
        mpos_with_trades[interval_no] = mpos_with_trades[interval_no] + trade_power[interval_no]
        # mpos_with_trades[interval_no] = trade_power[interval_no]

    # validate_discharge_trade(flex, mpos_with_trades, startinterval_no, duration)

    print(f'MPOs: {mpos_with_trades}')
    return mpos_with_trades

def generate_long_slow_charge_trade(flex: FlexibilityCalculation, mpos, endinterval_no):
    """
    Generates a multi-time-step trade, which ends at endinterval_no and previously
    takes as much charge power as possible until the min energy level is reached
    """

    print(f'End interval: {endinterval_no}\nFlexibility: {flex.flex_with_mpo}\nMPOs: {mpos}')
    earliest_charge_start = 0 #len(flex.flex_with_mpo.allowed_min_power)
    startinterval_no = 0
    duration = endinterval_no+1
    # l=range(endinterval_no+1, -1, -1)
    # print(l)
    for interval_no in range(endinterval_no, -1, -1):
        print(f'{interval_no} ',end='')
        # verify charge is possible
        if flex.flex_with_mpo.allowed_max_power[interval_no] < 0 or \
            flex.flex_with_mpo.allowed_max_energy_delta[interval_no] < flex.flex_with_mpo.allowed_min_energy_delta[interval_no-1]:
            earliest_charge_start = interval_no+1
            startinterval_no = earliest_charge_start
            duration = endinterval_no - earliest_charge_start+1
            print(f'\nEarliest charge start: {earliest_charge_start}')
            break
    # generate multi-time-step trade
    trade_power = [0.0]*len(flex.flex_with_mpo.allowed_max_power)
    trade_energy_delta = [0.0]*(len(trade_power))
    trade_energy_delta[endinterval_no] = flex.flex_with_mpo.allowed_max_energy_delta[endinterval_no]

    if endinterval_no >= earliest_charge_start:
        for interval_no in range(endinterval_no, earliest_charge_start-1, -1):
            print(f'{interval_no} ')
            print(f'Trade energy start: {trade_energy_delta}')
            print(f'Max Energy delta: {flex.flex_with_mpo.allowed_max_energy_delta[interval_no-1]}')
            print(f'Min Energy delta: {flex.flex_with_mpo.allowed_min_energy_delta[interval_no-1]}')
            if interval_no > 0:
                min_energy_delta_before = flex.flex_with_mpo.allowed_min_energy_delta[interval_no-1]
            elif interval_no == 0:
                min_energy_delta_before = 0
            print(f'Min energy delta beforce current interval: {min_energy_delta_before}')
            if trade_energy_delta[interval_no] < min_energy_delta_before:
             # or trade_energy_delta[interval_no] < flex.flex_with_mpo.allowed_min_energy_delta[interval_no-1]:
                # end trade if energy level exceeds limit
                startinterval_no = interval_no+1
                duration = endinterval_no - startinterval_no+1
                print(f'Break due to invalid energy. Duration: {duration}')
                print(f'Break trade power: {trade_power}')
                break

            power_allowed_by_power = flex.flex_with_mpo.allowed_max_power[interval_no]
            power_allowed_by_energy = (trade_energy_delta[interval_no] - \
                min_energy_delta_before) / 900*3600

            power_this_interval = min(power_allowed_by_power, power_allowed_by_energy)
            print(f'Power this inverval: {power_this_interval}')
            if power_this_interval < flex.flex_with_mpo.allowed_min_power[interval_no]:
                # end trade if power range is left
                startinterval_no = interval_no+1
                duration = endinterval_no - startinterval_no+1
                print(f'Break due to invalid power. Duration: {duration}')
                break

            # update trade_energy_delta
            trade_energy_delta[interval_no-1] = trade_energy_delta[interval_no] - power_this_interval*900/3600

            print(f'Current trade power in {interval_no}: {power_this_interval}')
            trade_power[interval_no] = power_this_interval
            assert trade_power[interval_no] >= 0

    print(f'Final trade power: {trade_power}\nFinal start interval: {startinterval_no}, final duration: {duration}')
    mpos_with_trades = mpos.copy()
    print('Start end', startinterval_no, endinterval_no)
    print(mpos_with_trades, trade_power)
    for interval_no in range(startinterval_no, endinterval_no+1):
        mpos_with_trades[interval_no] = mpos_with_trades[interval_no] + trade_power[interval_no]
        # mpos_with_trades[interval_no] = trade_power[interval_no]
    print(f'Final MPOs: {mpos_with_trades}')

    # validate_charge_trade(flex, mpos_with_trades, startinterval_no, duration)

    return mpos_with_trades

def generate_long_slow_discharge_trade(flex: FlexibilityCalculation, mpos, endinterval_no):
    """
    Generates a multi-time-step trade, which ends at endinterval_no and previously
    takes as much discharge power as possible until the max energy level is reached
    """
    # discharge trades
    print(f'End interval: {endinterval_no}\nFlexibility: {flex.flex_with_mpo}\nMPOs: {mpos}')
    earliest_discharge_start = 0 #len(flex.flex_with_mpo.allowed_min_power)
    startinterval_no = 0
    duration = endinterval_no+1
    # l=range(endinterval_no+1, -1, -1)
    # print(l)
    for interval_no in range(endinterval_no, -1, -1):
        print(f'{interval_no} ',end='')
        # verify discharge is possible
        if flex.flex_with_mpo.allowed_min_power[interval_no] > 0 or \
            flex.flex_with_mpo.allowed_min_energy_delta[interval_no] > flex.flex_with_mpo.allowed_max_energy_delta[interval_no-1]:
            earliest_discharge_start = interval_no+1
            startinterval_no = earliest_discharge_start
            duration = endinterval_no - earliest_discharge_start+1
            print(f'\nEarliest discharge start: {earliest_discharge_start}')
            break
    # generate multi-time-step trade
    trade_power = [0.0]*len(flex.flex_with_mpo.allowed_min_power)
    trade_energy_delta = [0.0]*(len(trade_power))
    trade_energy_delta[endinterval_no] = flex.flex_with_mpo.allowed_min_energy_delta[endinterval_no]

    if endinterval_no >= earliest_discharge_start:
        for interval_no in range(endinterval_no, earliest_discharge_start-1, -1):
            print(f'{interval_no} ')
            print(f'Trade energy start: {trade_energy_delta}')
            print(f'Max Energy delta: {flex.flex_with_mpo.allowed_max_energy_delta[interval_no-1]}')
            print(f'Min Energy delta: {flex.flex_with_mpo.allowed_min_energy_delta[interval_no-1]}')
            if interval_no > 0:
                max_energy_delta_before = flex.flex_with_mpo.allowed_max_energy_delta[interval_no-1]
            elif interval_no == 0:
                max_energy_delta_before = 0
            if trade_energy_delta[interval_no] > max_energy_delta_before:
             # or trade_energy_delta[interval_no] < flex.flex_with_mpo.allowed_min_energy_delta[interval_no-1]:
                # end trade if energy level exceeds limit
                startinterval_no = interval_no+1
                duration = endinterval_no - startinterval_no+1
                print(f'Break due to invalid energy. Duration: {duration}')
                break

            power_allowed_by_power = flex.flex_with_mpo.allowed_min_power[interval_no]
            power_allowed_by_energy = (trade_energy_delta[interval_no] - \
                max_energy_delta_before) / 900*3600

            power_this_interval = max(power_allowed_by_power, power_allowed_by_energy)
            print(f'Power this inverval: {power_this_interval}')
            if power_this_interval > flex.flex_with_mpo.allowed_max_power[interval_no]:
                # end trade if power range is left
                startinterval_no = interval_no+1
                duration = endinterval_no - startinterval_no+1
                print(f'Break due to invalid power. Duration: {duration}')
                break

            # update trade_energy_delta
            trade_energy_delta[interval_no-1] = trade_energy_delta[interval_no] - power_this_interval*900/3600

            print(f'Current trade power in {interval_no}: {power_this_interval}')
            trade_power[interval_no] = power_this_interval
            assert trade_power[interval_no] <= 0

    print(f'Final trade power: {trade_power}\nFinal start interval: {startinterval_no}, final duration: {duration}')
    mpos_with_trades = mpos.copy()
    print('Start end', startinterval_no, endinterval_no)
    print(mpos_with_trades, trade_power)
    for interval_no in range(startinterval_no, endinterval_no+1):
        mpos_with_trades[interval_no] = mpos_with_trades[interval_no] + trade_power[interval_no]
        # mpos_with_trades[interval_no] = trade_power[interval_no]
    print(f'Final MPOs: {mpos_with_trades}')

    # validate_discharge_trade(flex, mpos_with_trades, startinterval_no, duration)

    return mpos_with_trades

def validate_charge_trade(flex, mpos_with_trades, startinterval_no, duration):
    # validate trade
    if startinterval_no == 0:
        min_energy = 0
    else:
        min_energy = flex.flex_with_mpo.allowed_min_energy_delta[startinterval_no-1]

    for interval_no in range(startinterval_no, startinterval_no+duration):
        # validate trade

        max_power = flex.flex_with_mpo.allowed_max_power[interval_no]
        min_power = flex.flex_with_mpo.allowed_min_power[interval_no]
        assert max_power >= mpos_with_trades[interval_no] >= min_power, \
            f'Left allowed power range: {mpos_with_trades}, in interval: {interval_no}\n' \
            f'Planned trade: {mpos_with_trades}, begin at index: {startinterval_no}\nFlexibility: {flex.flex_with_mpo}'

        max_energy_delta = flex.flex_with_mpo.allowed_max_energy_delta[interval_no]
        min_energy_delta = flex.flex_with_mpo.allowed_min_energy_delta[interval_no]
        assert max_energy_delta >= min_energy + mpos_with_trades[interval_no]*900/3600 >= min_energy_delta, \
            f'Left allowed energy range: {mpos_with_trades}, in interval: {interval_no}\n' \
            f'Planned trade: {mpos_with_trades}, begin at index: {startinterval_no}\nFlexibility: {flex.flex_with_mpo}'

        min_energy = min_energy + mpos_with_trades[interval_no]*900/3600

def validate_discharge_trade(flex, mpos_with_trades, startinterval_no, duration):
    # validate trade
    if startinterval_no == 0:
        max_energy = 0
    else:
        max_energy = flex.flex_with_mpo.allowed_max_energy_delta[startinterval_no-1]

    for interval_no in range(startinterval_no, startinterval_no+duration):
        # validate trade

        max_power = flex.flex_with_mpo.allowed_max_power[interval_no]
        min_power = flex.flex_with_mpo.allowed_min_power[interval_no]
        assert max_power >= mpos_with_trades[interval_no] >= min_power, \
            f'Left allowed power range: {mpos_with_trades}, in interval: {interval_no}\n' \
            f'Planned trade: {mpos_with_trades}, begin at index: {startinterval_no}\nFlexibility: {flex.flex_with_mpo}'

        max_energy_delta = flex.flex_with_mpo.allowed_max_energy_delta[interval_no]
        min_energy_delta = flex.flex_with_mpo.allowed_min_energy_delta[interval_no]
        assert max_energy_delta >= max_energy + mpos_with_trades[interval_no]*900/3600 >= min_energy_delta, \
            f'Left allowed energy range: {mpos_with_trades}, in interval: {interval_no}\n' \
            f'Planned trade: {mpos_with_trades}, begin at index: {startinterval_no}\nFlexibility: {flex.flex_with_mpo}'

        max_energy = max_energy + mpos_with_trades[interval_no]*900/3600
        print(max_energy)

def generate_long_medium_charge_trade(flex: FlexibilityCalculation, mpos, startinterval_no, duration):
    """
    Generate a multi-time-step trade, which starts at startinterval_no and of
    duration length, only if at all corresponding time intervals charging is
    allowed.
    The trade takes as much charge power as possible until a dip in the allowed
    energy is detected in the near future. Then it approaches the dip with an
    equal share each time step.
    """
# charge trades
    charge_possible = True
    for d in range(duration):
        # verify charge is possible
        if flex.flex_with_mpo.allowed_max_power[startinterval_no+d] < 0:
            charge_possible = False
    # generate multi-time-step trade
    trade_power = [0.0]*duration
    print(f'Charge possible: {charge_possible}')
    if charge_possible:
        trade_energy_delta = [0.0]*(duration+1)
        if startinterval_no == 0:
            trade_energy_delta[0] = 0
        else:
            trade_energy_delta[0] = flex.flex_with_mpo.allowed_min_energy_delta[startinterval_no-1]
        for interval_no in range(duration):
            # look into future, how much energy can be used for trade of duration time steps
            useable_energy_delta = [x-trade_energy_delta[interval_no] for x in flex.flex_with_mpo.allowed_max_energy_delta[startinterval_no+interval_no:startinterval_no+duration]]

            # detect most critical energy delta in near future and its index
            useable_energy = min(useable_energy_delta)
            useable_energy_index = useable_energy_delta.index(useable_energy)
            # plan equal share of energy each time step
            if isinstance(useable_energy_index,list):
                useable_energy_index = useable_energy_index[-1]
            to_be_used_energy = useable_energy / (useable_energy_index+1)
            # make sure, allowed energy range is not left
            minimum_energy_next_step = flex.flex_with_mpo.allowed_min_energy_delta[startinterval_no+interval_no]
            if to_be_used_energy < minimum_energy_next_step - trade_energy_delta[interval_no]:
                to_be_used_energy = minimum_energy_next_step - trade_energy_delta[interval_no]

            to_be_used_power = to_be_used_energy/900*3600
            if to_be_used_power < flex.flex_with_mpo.allowed_min_power[startinterval_no+interval_no]:
                trade_power[interval_no] = flex.flex_with_mpo.allowed_min_power[startinterval_no+interval_no]
            elif to_be_used_power > flex.flex_with_mpo.allowed_max_power[startinterval_no+interval_no]:
                trade_power[interval_no] = flex.flex_with_mpo.allowed_max_power[startinterval_no+interval_no]
            else:
                trade_power[interval_no] = to_be_used_power
            # update trade_energy_delta
            trade_energy_delta[interval_no+1] = trade_energy_delta[interval_no] + trade_power[interval_no]*900/3600

    mpos_with_trades = mpos.copy()

    if charge_possible:
        print(f'Trade: {trade_power}')
        for interval_no in range(duration):
            mpos_with_trades[startinterval_no+interval_no] = mpos_with_trades[startinterval_no+interval_no] + trade_power[interval_no]
            # mpos_with_trades[startinterval_no+interval_no] = trade_power[interval_no]
        print(f'MPOs: {mpos_with_trades}')
        validate_charge_trade(flex, mpos_with_trades, startinterval_no, duration)

    return mpos_with_trades

def generate_long_medium_discharge_trade(flex: FlexibilityCalculation, mpos, startinterval_no, duration):
    """
    Generate a multi-time-step trade, which starts at startinterval_no and of
    duration length, only if at all corresponding time intervals charging is
    allowed.
    The trade takes as much charge power as possible until a dip in the allowed
    energy is detected in the near future. Then it approaches the dip with an
    equal share each time step.
    """
# charge trades
    discharge_possible = True
    for d in range(duration):
        # verify discharge is possible
        if flex.flex_with_mpo.allowed_min_power[startinterval_no+d] > 0:
            discharge_possible = False
    # generate multi-time-step trade
    trade_power = [0.0]*duration
    print(f'Discharge possible: {discharge_possible}')
    if discharge_possible:
        trade_energy_delta = [0.0]*(duration+1)
        if startinterval_no == 0:
            trade_energy_delta[0] = 0
        else:
            trade_energy_delta[0] = flex.flex_with_mpo.allowed_max_energy_delta[startinterval_no-1]
        for interval_no in range(duration):
            # look into future, how much energy can be used for trade of duration time steps
            useable_energy_delta = [x-trade_energy_delta[interval_no] for x in flex.flex_with_mpo.allowed_min_energy_delta[startinterval_no+interval_no:startinterval_no+duration]]

            # detect most critical energy delta in near future and its index
            useable_energy = min(useable_energy_delta)
            useable_energy_index = useable_energy_delta.index(useable_energy)
            # plan equal share of energy each time step
            if isinstance(useable_energy_index,list):
                useable_energy_index = useable_energy_index[-1]
            to_be_used_energy = useable_energy / (useable_energy_index+1)
            # make sure, allowed energy range is not left
            maximum_energy_next_step = flex.flex_with_mpo.allowed_max_energy_delta[startinterval_no+interval_no]
            if to_be_used_energy > maximum_energy_next_step - trade_energy_delta[interval_no]:
                to_be_used_energy = maximum_energy_next_step - trade_energy_delta[interval_no]

            to_be_used_power = to_be_used_energy/900*3600
            if to_be_used_power < flex.flex_with_mpo.allowed_min_power[startinterval_no+interval_no]:
                trade_power[interval_no] = flex.flex_with_mpo.allowed_min_power[startinterval_no+interval_no]
            elif to_be_used_power > flex.flex_with_mpo.allowed_max_power[startinterval_no+interval_no]:
                trade_power[interval_no] = flex.flex_with_mpo.allowed_max_power[startinterval_no+interval_no]
            else:
                trade_power[interval_no] = to_be_used_power
            # update trade_energy_delta
            trade_energy_delta[interval_no+1] = trade_energy_delta[interval_no] + trade_power[interval_no]*900/3600

    mpos_with_trades = mpos.copy()
    if discharge_possible:
        print(f'Trade: {trade_power}')
        for interval_no in range(duration):
            mpos_with_trades[startinterval_no+interval_no] = mpos_with_trades[startinterval_no+interval_no] + trade_power[interval_no]
            # mpos_with_trades[startinterval_no+interval_no] = trade_power[interval_no]
        print(f'MPOs: {mpos_with_trades}')
        validate_discharge_trade(flex, mpos_with_trades, startinterval_no, duration)

    return mpos_with_trades
