

def assert_disaggregation_possible(flex_calculator1, flex_calculator2,
        flex_before_trades1, flex_before_trades2, p1, p2, placed_trade):

    mpos_with_trades1 = [0.0]*len(placed_trade)
    mpos_with_trades2 = [0.0]*len(placed_trade)

    for interval_no in range(len(placed_trade)):
        # share for flex1
        if placed_trade[interval_no] > 0 and flex_before_trades1.flex_with_mpo.allowed_max_power[interval_no] > 0:
            mpos_with_trades1[interval_no] = min(flex_before_trades1.flex_with_mpo.allowed_max_power[interval_no],placed_trade[interval_no])
        elif placed_trade[interval_no] < 0 and flex_before_trades1.flex_with_mpo.allowed_min_power[interval_no] < 0:
            mpos_with_trades1[interval_no] = max(flex_before_trades1.flex_with_mpo.allowed_min_power[interval_no],placed_trade[interval_no])
        # share for flex2
        mpos_with_trades2[interval_no] = placed_trade[interval_no] - mpos_with_trades1[interval_no]

        print(f'MPOs 1: {mpos_with_trades1}, MPOs 2: {mpos_with_trades2}')
        # recalculate flex1/2
        flex_before_trades1 = \
            flex_calculator1.calculate_total_flex(curr_soc=p1.start_soc, passed_time_of_curr_interval=p1.passed_time,
            avg_p_bat_of_curr_interval=p1.avg_p_bat,
            mpos=mpos_with_trades1, final_min_soc=p1.final_min_soc,
            final_max_soc=p1.final_max_soc, forecast=p1.forecast, p_max_ps=p1.p_max,
            t_start=0)
        flex_before_trades2 = \
            flex_calculator2.calculate_total_flex(curr_soc=p2.start_soc, passed_time_of_curr_interval=p2.passed_time,
            avg_p_bat_of_curr_interval=p2.avg_p_bat,
            mpos=mpos_with_trades2, final_min_soc=p2.final_min_soc,
            final_max_soc=p2.final_max_soc, forecast=p2.forecast, p_max_ps=p2.p_max,
            t_start=0)

        print(f'Remaining flexibility 1: {flex_before_trades1.flex_with_mpo}, \nRemaining flexibility 2: {flex_before_trades2.flex_with_mpo}\n')

        assert flex_before_trades1.problems == [], \
            f'{p1}\nMPOs 1: {mpos_with_trades1}\n' \
            f'Problems 1: {flex_before_trades1.problems}'
        assert flex_before_trades2.problems == [], \
            f'{p2}\nMPOs 2: {mpos_with_trades2}\n' \
            f'Problems 2: {flex_before_trades2.problems}'
