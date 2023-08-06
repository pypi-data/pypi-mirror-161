"""
This is the flexibility calculation module. It belongs to the core of the
plex module of a storage agent and handles all the internal logic for
calculating flexibility.
"""

import time
from math import ceil as ceil
from math import floor as floor
from typing import List, Tuple, Optional
import logging
from .data_classes import FlexibilityCalculation, Flexibility, Problem


module = "amplify"
name = "flex_calculation"
logger = logging.getLogger(f'{module}.{name}')

class FlexCalculator:
    """
    Flex calculator is able to calculate all the 4 steps necessary for
    the interval flexibility calculation of the plex module.
    """

    def __init__(self, *, max_p_bat: int, min_p_bat: int, capacity_energy: int,
                 efficiency_charge: float, efficiency_discharge: float,
                 soh: float = 1,
                 problem_detection_horizon: int = 4 * 60 * 60):
        """

        :param max_p_bat: Maximum power of the battery (>0) [W]
        :param min_p_bat: Minimum power of the battery (<0) [W]
        :param capacity_energy: Capacity of the battery [Wh]
        :param efficiency_charge: Efficiency of charging [0,1]
        :param efficiency_discharge: Efficiency of discharging [0,1]
        :param soh: The state of health of the battery [0,1]. It reduces
        the usuable capacity of the battery
        :param problem_detection_horizon: Horizon until when problems are
        Not ignored. all problems after that horizon are ignored
        """
        self.max_p_bat = max_p_bat  # [W]
        self.min_p_bat = min_p_bat  # [W]
        self.nominal_capacity = capacity_energy  # [W]
        self.capacity_energy = capacity_energy * soh  # [Wh]
        self.efficiency_charge = efficiency_charge  # [0,1]
        self.efficiency_discharge = efficiency_discharge  # [0,1]
        self.soh = soh
        self.problem_detection_horizon = problem_detection_horizon  # [s]

        # # DEBUG:
        self.PPR_print = False

    def update(self, *, max_p_bat: int, min_p_bat: int,
               soh: float):
        """
        Updates the flex calculator
        :param max_p_bat: Maximum power of the battery (>0) [W]
        :param min_p_bat: Minimum power of the battery (<0) [W]
        :param soh: The state of health of the battery [0,1]
        """
        self.max_p_bat = max_p_bat
        self.min_p_bat = min_p_bat
        self.soh = soh
        # adapt capacity due to SoH
        self.capacity_energy = soh * self.nominal_capacity

    def power_to_soc_diff(self, *, power: int, duration: int = 15 * 60) -> float:
        """
        Calculates the difference in SoC according to the given external
        power value over time considering efficiency
        :param power: the power value [W]
        :param duration: the time of the power value [s] (default 900 seconds)
        :return: the change in SoC [-1, 1]
        """

        if power > 0:
            # charging is less than the external power
            power_at_bat = power * self.efficiency_charge  # [W]
        else:
            # discharging is greater than the external power
            power_at_bat = power / self.efficiency_discharge  # [W]

        # energy difference is power * duration / one hour
        energy_diff = power_at_bat * duration / (60 * 60)  # [Wh]
        soc_diff = energy_diff / self.capacity_energy  # [-1,1]

        return soc_diff

    def soc_diff_to_power(self, *, soc_diff: float, duration: int = 15 * 60) \
            -> int:
        """
        Calculates the expected external power value given a change in the
        SoC and a time period
        :param soc_diff: the difference in the soc [-1, 1]
        :param duration: the time of the power value [s] (default 900 seconds)
        :return: the external power value [W]
        """

        energy_diff = soc_diff * self.capacity_energy  # [Wh]
        if energy_diff > 0:
            total_energy = energy_diff / self.efficiency_charge  # [Wh]
        else:
            total_energy = energy_diff * self.efficiency_discharge  # [Wh]

        # consider the time period
        external_power = total_energy * 60 * 60 / duration  # [W]

        return int(round(external_power))

    def calculate_start_soc_of_current_interval(
            self, *, curr_soc: float, avg_p_bat_of_curr_interval: int,
            passed_time_of_curr_interval: int) -> float:
        """
        Step 0
        Correct the current soc by the a difference that would have been caused,
        if the storage had consumed/generated the average power constantly.
        :param curr_soc: the current soc [0,1]
        :param avg_p_bat_of_curr_interval: average storage power during the
        current interval [W]
        :param passed_time_of_curr_interval: passed time within
        the current interval [s]
        :return start_soc: a fictive soc at the start of the interval [0,1]
        """
        soc_change_from_interval_start = self.power_to_soc_diff(
            power=avg_p_bat_of_curr_interval,
            duration=passed_time_of_curr_interval)
        start_soc = curr_soc - soc_change_from_interval_start
        # TODO start_soc has to be in [0,1]. Errors could be possible due to the parametrized constant efficiencies.
        start_soc = min(1., start_soc)
        start_soc = max(0., start_soc)

        return start_soc

    def calculate_available_power_range(self, *, forecast: List[Optional[int]],
                                        p_max_ps: List[int],
                                        mpos: List[int],
                                        avg_p_bat_of_curr_interval: int,
                                        passed_time_of_curr_interval: int,
                                        res: int,
                                        critical_interval: int = 0) \
            -> Tuple[List[int], List[int], List[Problem]]:
        """
        Step 1
        Calculates the available power range (min of power diff and p_max).
        The power in the current interval respects the already realized storage
        power.
        :param forecast: the load forecast [W]
        :param p_max_ps: the p_max for peak shaving per interval [W]
        :param avg_p_bat_of_curr_interval: average storage power during the
        current interval until now [W]
        :param res: resolution of the intervals [s], defaults to 900
        :param passed_time_of_curr_interval: Number of seconds passed within
        the current interval
        :param critical_interval: first interval without problem detection
        :return: power range max and power range min and Problems
        """

        # synchronize lengths of vectors from forecast, peak shaving power
        # and mpos
        logger.debug(f'{len(forecast)}, {len(p_max_ps)}, {len(mpos)}')
        assert len(forecast) == len(p_max_ps) == len(mpos), \
            (len(forecast), len(p_max_ps), len(mpos))
        problems: List[Problem] = []
        power_diff = [x - y if y is not None else None
                      for x, y in zip(p_max_ps, forecast)]
        # get power diff
        # power range for p_max is min of power diff and physical constraint
        available_max_power = [min(x, self.max_p_bat) if x is not None
                               else self.max_p_bat for x in power_diff]
        # power range is determined by physical constraint
        # (without multi purpose)
        available_min_power = [self.min_p_bat] * len(power_diff)

        # (possibly) reduce power in current interval
        remaining_time = res - passed_time_of_curr_interval
        p_curr_max = (avg_p_bat_of_curr_interval * passed_time_of_curr_interval
                      + self.max_p_bat * remaining_time) / res

        available_max_power[0] = min(available_max_power[0], int(p_curr_max))

        p_curr_min = (avg_p_bat_of_curr_interval * passed_time_of_curr_interval
                      + self.min_p_bat * remaining_time) / res
        available_min_power[0] = max(available_min_power[0], int(p_curr_min))

        # check for problems:
        for interval_no, max_value in enumerate(available_max_power):
            if interval_no == 0:
                current_p_min = int(p_curr_min)
            else:
                current_p_min = self.min_p_bat
            if max_value < current_p_min:
                available_max_power[interval_no] = current_p_min
                if interval_no < critical_interval:
                    if self.PPR_print:
                        print('Step 1: Problem P1.1 registered.')
                    problems.append(Problem(
                        problem_type='P1.1', interval_no=interval_no,
                        negotiation_required=False, required=max_value,
                        realizable=current_p_min))


        # respect trades
        for interval_no, mpo_value in enumerate(mpos):
            # print(str((interval_no,mpo_value)))
            if mpo_value > 0:
                # charge trade
                if mpo_value > available_max_power[interval_no]:
                    # print(f'MPO>0: {mpo_value}')
                    # we cannot fulfill trade, do as much as you can
                    available_min_power[interval_no] = \
                        available_max_power[interval_no]
                    if interval_no < critical_interval:
                        # create problem
                        if self.PPR_print:
                            print('Step 1: Problem P1.2 registered (charge).')
                        problems.append(Problem(
                            problem_type='P1.2', interval_no=interval_no,
                            negotiation_required=True, required=mpo_value,
                            realizable=available_max_power[interval_no]))

                else:
                    # we can fulfill trade, so we should at least provide the
                    # power
                    available_min_power[interval_no] = \
                        max(mpos[interval_no], available_min_power[interval_no])


            elif mpo_value < 0:
                # print(str((interval_no,mpo_value, available_min_power[interval_no])))
                # discharge trade
                if mpo_value < available_min_power[interval_no]:
                    # we cannot fulfill trade, do as little as you can
                    available_max_power[interval_no] = available_min_power[interval_no]
                    if interval_no < critical_interval:
                        if self.PPR_print:
                            print('Step 1: Problem P1.2 registered (discharge).')
                        problems.append(Problem(
                            problem_type='P1.2', interval_no=interval_no,
                            negotiation_required=True, required=mpo_value,
                            realizable=available_min_power[interval_no]))
                else:
                    # we can fulfill trade, so we should at least provide the
                    # power
                    # print(str((interval_no,mpo_value)))
                    available_max_power[interval_no] = \
                        min(mpos[interval_no], available_max_power[interval_no])
        # print('Max: '+str(available_max_power))
        # print('Min: '+str(available_min_power))

        return available_max_power, available_min_power, problems

    def calculate_soc_flexibility_backward(
            self, *, available_max_power: List[int],
            available_min_power: List[int],
            final_min_soc: float = 0., final_max_soc: float = 1.,
            res: int = 15 * 60) -> Tuple[List[float], List[float]]:
        """
        Step 2b: Calculate the required SoC range for the end of each
        interval
        ATTENTION: This has changed to the end of the interval
        :param available_max_power: the maximum available power
        calculated in step 1 [W]
        :param available_min_power: the minimum available power
        calculated in step 1 [W]
        :param final_min_soc: the required min SoC at the end of
        the planning horizon [0,1], defaults to 0
        :param final_max_soc: the required max SoC at the end of the
         planning horizon [0,1], defaults to 1
        :param res: the resolution of the intervals [s], defaults to 900
        :return: max_required_soc and min_required_soc for the end of each
        interval
        """

        assert len(available_max_power) == len(available_min_power)

        # initialize return lists (-1. is just a placeholder)
        period = len(available_max_power)
        required_max_soc = [-1.] * period
        required_min_soc = [-1.] * period

        max_soc_at_interval_start = final_max_soc
        min_soc_at_interval_start = final_min_soc

        # starts at the last interval, until interval 1
        for interval_no in range(period - 1, 0, -1):
            # required start soc values of next interval are required end
            # soc values for this interval
            max_soc_at_interval_end = max_soc_at_interval_start
            min_soc_at_interval_end = min_soc_at_interval_start

            # get maximum soc change on the basis of the available max power
            # (can be < 0 if discharging is required)
            max_soc_change = self.power_to_soc_diff(
                power=available_max_power[interval_no], duration=res
            )
            # get minimum soc change on the basis of the available min power
            # (can be > 0 if charging is required)
            min_soc_change = self.power_to_soc_diff(
                power=available_min_power[interval_no], duration=res
            )

            # get max soc at interval start (cannot be > 1)
            max_soc_at_interval_start = min(1.0, max_soc_at_interval_end -
                                            min_soc_change)

            # get min soc at interval start (cannot be < 0)
            min_soc_at_interval_start = max(0.0, min_soc_at_interval_end -
                                            max_soc_change)

            if max_soc_at_interval_start < 0:
                # no problem detection here so min is 0
                max_soc_at_interval_start = 0

            if min_soc_at_interval_start > 1:
                # no problem detection here so max is 1
                min_soc_at_interval_start = 1

            # the required at the end of last interval must be this start
            required_max_soc[interval_no - 1] = max_soc_at_interval_start
            required_min_soc[interval_no - 1] = min_soc_at_interval_start

        # add the final socs to the end of the list
        required_max_soc[-1] = final_max_soc
        required_min_soc[-1] = final_min_soc

        return required_max_soc, required_min_soc

    def calculate_soc_flexibility_forward(
            self, *, available_max_power: List[int],
            available_min_power: List[int],
            start_soc: float, res: int = 15 * 60, critical_interval_max: int = 0,
            critical_interval_min: int = 0, ) \
            -> Tuple[List[float], List[float], Tuple[float, float]]:
        """
        Step 2a: Calculate the reachable SoC range at the end of each
        interval
        :param available_max_power: the maximum available power
        calculated in step 1 [W]
        :param available_min_power: the minimum available power
        calculated in step 1 [W]
        :param start_soc: the soc of the battery at the start of the
        first interval [0,1]
        :param res: the resolution of the intervals [s], defaults to 900
        :param critical_interval_max: first interval without problem detection
        for max_soc
        :param critical_interval_min: first interval without probme detectio
        for min_soc
        :return: the reachable SoC at the beginning of each interval and
        the min of max_soc and the max of min_soc within the critical period
        """
        assert len(available_max_power) == len(available_min_power)
        period = len(available_min_power)

        reachable_max_soc = [-1.] * period
        reachable_min_soc = [-1.] * period

        # Minimum and maximum are defined by soc_start
        min_soc_at_interval_end = start_soc
        max_soc_at_interval_end = start_soc

        # default values for detecting extrem values in SoC range
        min_max_soc = [(0, 0)]
        max_min_soc = [(0, 1)]
        append_min_max_soc = False
        append_max_min_soc = False

        for current_interval in range(period):
            # start values are the end values of last interval
            min_soc_at_interval_start = min_soc_at_interval_end
            max_soc_at_interval_start = max_soc_at_interval_end

            # # another extrem value can occur, if max_soc==1 or min_soc==0
            # if append_min_max_soc and max_soc_at_interval_end == 1:
            #     min_max_soc[len(min_max_soc)]

            # get maximum soc change on the basis of the available max power
            # (can be < 0 if discharging is required)
            max_soc_change = self.power_to_soc_diff(
                power=available_max_power[current_interval], duration=res
            )
            # print('max_soc_change: '+str(max_soc_change))
            # get minimum soc change on the basis of the available min power
            # (can be > 0 if charging is required)
            min_soc_change = self.power_to_soc_diff(
                power=available_min_power[current_interval], duration=res
            )

            # what soc can be reached at the end of the interval
            max_soc_at_interval_end = min(1.0, max_soc_at_interval_start +
                                          max_soc_change)
            min_soc_at_interval_end = max(0.0, min_soc_at_interval_start +
                                          min_soc_change)

            # too low max_SoC reached
            if max_soc_at_interval_end < 0:
                # adapt soc, if no ppr detection
                if current_interval >= critical_interval_max:
                    max_soc_at_interval_end = 0
                else:
                    # store as problem, if ppr detection
                    if max_soc_at_interval_end < min_max_soc[-1][1]:
                        min_max_soc[-1] = \
                            (current_interval, max_soc_at_interval_end)
                        append_min_max_soc = True  # next extrem value possible
            if append_min_max_soc and max_soc_at_interval_end == 1:
                # append new min_max_soc, if storage charged in between
                min_max_soc.append((0, 0))
                append_min_max_soc = False

            # too high min_SoC reached
            if min_soc_at_interval_end > 1:
                # adapt soc if no ppr detection
                if current_interval >= critical_interval_min:
                    min_soc_at_interval_end = 1
                else:
                    # store as problem if ppr detection
                    if min_soc_at_interval_end > max_min_soc[-1][1]:
                        max_min_soc[-1] = \
                            (current_interval, min_soc_at_interval_end)
                        append_max_min_soc = True  # next extrem value possible
                if append_max_min_soc and min_soc_at_interval_end == 0:
                    # append new max_min_soc, if storage charged in between
                    max_min_soc.append((0, 1))
                    append_max_min_soc = False

            reachable_min_soc[current_interval] = min_soc_at_interval_end
            reachable_max_soc[current_interval] = max_soc_at_interval_end

        # remove last min_max_soc and max_min_soc, if not critical_interval
        if min_max_soc[-1][1] >= 0:
            min_max_soc.pop()
        if max_min_soc[-1][1] <= 1:
            max_min_soc.pop()

        return reachable_max_soc, reachable_min_soc, (min_max_soc, max_min_soc)

    @classmethod
    def calculate_allowed_soc_range(
            cls, *, required_max_soc: List[float],
            required_min_soc: List[float], reachable_max_soc: List[float],
            reachable_min_soc: List[float], critical_interval: int = 0, ) \
            -> Tuple[List[float], List[float]]:
        """
        Step 2c: Calculate the allowed soc range at the end of each interval
        :param required_max_soc: Required max socs (calculated in step 2b)
        :param required_min_soc: Required min socs (calculated in step 2b)
        :param reachable_max_soc: Reachable max socs (calculated in step 2a)
        :param reachable_min_soc: Reachable min socs (calculated in step 2a)
        :param critical_interval: first interval without problem detection
        :return: allowed_max_soc, allowed_min_soc
        """

        # all lists have to have the same length
        assert len(required_max_soc) == len(required_min_soc) == \
               len(reachable_max_soc) == len(reachable_min_soc), \
            f'Length of lists from step 2 and 3 are not equal, ' \
            f'len of required is {len(required_max_soc)} ' \
            f'and len of reachable is {len(reachable_max_soc)}'

        period = len(required_min_soc)

        allowed_min_soc = []
        allowed_max_soc = []

        for current_interval in range(period):
            # remove problems, in which case these intervals do not
            # overlap! Possible in case of very large, unshavable peaks
            if required_max_soc[current_interval] < \
                    reachable_min_soc[current_interval]:
                required_max_soc[current_interval] = \
                    reachable_min_soc[current_interval]
            if required_min_soc[current_interval] > \
                    reachable_max_soc[current_interval]:
                required_min_soc[current_interval] = \
                    reachable_max_soc[current_interval]

            # min SoC is max of min_required and min_reachable
            allowed_min_soc.append(
                max(required_min_soc[current_interval],
                    reachable_min_soc[current_interval])
            )

            # max SoC is min of max_required and max_reachable
            allowed_max_soc.append(
                min(required_max_soc[current_interval],
                    reachable_max_soc[current_interval])
            )

        return allowed_max_soc, allowed_min_soc

    def convert_soc_range_to_energy_flex(
            self, *, max_soc: List[float], min_soc: List[float],
            start_soc: float, max_power: List[int], min_power: List[int]) \
            -> Tuple[List[int], List[int]]:
        """
        Step 3: Converts the allowed soc range to energy flexibility
        at the end of each interval, which
        will be communicated to the aggregator
        The result communicates the available energy flexibility at the END of
        each interval.
        In order to round the float values appropriately to integers, the
        direction of the allowed power flexibility is considered.
        :param max_soc: list of max soc values [0,1]
        :param min_soc: list of min soc values [0,1]
        :param start_soc: the starting soc [0,1]
        :return: max_energy_delta, min_energy_delta
        """
        assert len(max_soc) == len(min_soc) == len(max_power) == len(min_power)
        max_energy_delta = []
        min_energy_delta = []

        for interval_no in range(len(max_soc)):
            current_max_soc = max_soc[interval_no]
            current_min_soc = min_soc[interval_no]
            if min_power[interval_no] > 0: # obligatory charge:
                current_max_energy_delta = \
                    int(floor((current_max_soc - start_soc) * \
                    self.capacity_energy))
                current_min_energy_delta = \
                    min(current_max_energy_delta,
                        int(ceil((current_min_soc - start_soc) * \
                        self.capacity_energy))
                    )
            else: # obligatory discharge or standard case
                current_min_energy_delta = \
                    int(ceil((current_min_soc - start_soc) * \
                    self.capacity_energy))
                current_max_energy_delta = \
                    max(current_min_energy_delta,
                        int(floor((current_max_soc - start_soc) * \
                        self.capacity_energy))
                    )
            max_energy_delta.append(current_max_energy_delta)
            min_energy_delta.append(current_min_energy_delta)

        return max_energy_delta, min_energy_delta

    def increase_min_soc_by_discharge_efficiency_losses(
            self, *, max_soc: List[float], min_soc: List[float],
            allowed_max_power: List[float], allowed_min_power: List[float],
            res: int = 15 * 60, start_soc: float, critical_interval: int = 0,
            debug_print: bool) \
            -> Tuple[List[int], List[int]]:
        """
        Step 3: increases the min_soc to respect the discharge efficiency
        :param max_soc: list of max soc values [0,1]
        :param min_soc: list of min soc values [0,1]
        :param allowed_max_power: allowed max power calculated in step 4
        :param allowed_min_power: allowed min power calculated in step 4
        :param res: Resolution [s], defaults to 15 * 60
        :param start_soc: the starting soc [0,1]
        :param critical_interval: first interval without problem detection
        :return: max_soc, increased_min_soc
        """

        assert len(min_soc) == len(max_soc) == \
               len(allowed_min_power) == len(allowed_max_power)

        period = len(allowed_max_power)

        increased_max_soc = [0.0] * len(min_soc)
        increased_min_soc = [0.0] * len(min_soc)

        for current_interval in range(period):
            if current_interval == 0:
                increased_min_soc[current_interval] = min_soc[current_interval]

            else:
                # go back in time
                for earlier_interval in range(current_interval, -1, -1):
                    if earlier_interval == current_interval:
                        # initialize max_soc_before_current_min
                        # which contains the max_soc from which min_soc
                        # of the current_interval can be reached
                        max_soc_before_current_min = \
                            min_soc[current_interval]
                        max_soc_before_current_min_power = \
                            min_soc[current_interval]
                    else:
                        # increase max_soc_before_current_min_power
                        # due to discharge power
                        max_soc_before_current_min_power = \
                            max_soc_before_current_min_power - \
                            min(0, allowed_min_power[earlier_interval]) / \
                            self.efficiency_discharge * res / self.capacity_energy
                        # set max_soc_before_current_min
                        max_soc_before_current_min = min(
                            max_soc[earlier_interval],
                            max_soc_before_current_min_power
                        )
                        # stop in case of mandatory charging or
                        # in case of a lower earlier max soc
                        if allowed_min_power[earlier_interval] > 0 or \
                            (max_soc_before_current_min > max_soc[earlier_interval-1]
                            and earlier_interval >= 0):
                            break
                if debug_print:
                    print(f'Max SoC before current min in {current_interval}: {max_soc_before_current_min}')
                delta_soc_till_current_interval = \
                    max_soc_before_current_min - min_soc[current_interval]
                delta_soc_till_current_interval = \
                    max(0, delta_soc_till_current_interval)
                # # Case 1: Increase by (1/eta-1)
                increased_min_soc[current_interval] = \
                    min_soc[current_interval] + \
                    delta_soc_till_current_interval * \
                    (1/self.efficiency_discharge-1)
                # # Case 2: Increase by (1-eta)
                # increased_min_soc[current_interval] = \
                #     min_soc[current_interval] + \
                #     delta_soc_till_current_interval * \
                #     (1 - self.efficiency_discharge)
                # # Case 3: Don't increase
                # increased_min_soc[current_interval] = min_soc[current_interval]

            # limit max_soc by min_soc
            increased_max_soc[current_interval] = \
                max(increased_min_soc[current_interval],
                    max_soc[current_interval])
        if debug_print:
            print(f'Initial max soc: {max_soc}')
            print(f'Initial min soc: {min_soc}')
            print(f'Increased max soc: {increased_max_soc}')
            print(f'Increased min soc: {increased_min_soc}')
        return increased_max_soc, increased_min_soc

    def calculate_allowed_power_flexibility(
            self, *, allowed_max_soc: List[float],
            allowed_min_soc: List[float], available_max_power: List[int],
            available_min_power: List[int], res: int = 15 * 60,
            start_soc: float, critical_interval: int = 0) \
            -> Tuple[List[int], List[int]]:
        """
        Step 4: calculates the allowed power range
        :param allowed_max_soc: Allowed max SoC calculated in step 3
        :param allowed_min_soc: Allowed min SoC calculated in step 3
        :param available_max_power: available max power calculated in step 1
        :param available_min_power: available min power calculated in step 1
        :param res: Resolution [s], defaults to 15 * 60
        :param start_soc: the start soc at the beginning of interval 0
        :param critical_interval: first interval without problem detection
        :return: allowed_max_power, allowed_min_power
        """

        assert len(allowed_min_soc) == len(allowed_max_soc) == \
               len(available_min_power) == len(available_max_power)

        period = len(available_max_power)

        allowed_max_power = []
        allowed_min_power = []

        for current_interval in range(period):
            if current_interval == 0:
                max_soc_diff = allowed_max_soc[current_interval] - start_soc
                min_soc_diff = allowed_min_soc[current_interval] - start_soc
            else:
                # get maximum and minimum SoC diff for this interval
                max_soc_diff = allowed_max_soc[current_interval] - \
                               allowed_min_soc[current_interval - 1]

                min_soc_diff = allowed_min_soc[current_interval] - \
                               allowed_max_soc[current_interval - 1]

            # convert SoC diff to power per interval
            max_power_from_soc = self.soc_diff_to_power(soc_diff=max_soc_diff,
                                                        duration=res)
            min_power_from_soc = self.soc_diff_to_power(soc_diff=min_soc_diff,
                                                        duration=res)

            # maximum allowed power is min of max_power_from_soc
            # and power_range_max
            allowed_max_power.append(
                min(max_power_from_soc, available_max_power[current_interval])
            )

            # minimum allowed power is max of min_power_from_soc
            # and power_range_min
            allowed_min_power.append(
                max(min_power_from_soc, available_min_power[current_interval]))

            # remove problems, in which case these powers do
            # overlap! Possible in case of very large, unshavable peaks
            if allowed_max_power[-1] < allowed_min_power[-1]:
                if allowed_max_power[-1] > 0:
                    allowed_min_power[-1] = allowed_max_power[-1]
                elif allowed_min_power[-1] < 0:
                    allowed_max_power[-1] = allowed_min_power[-1]
                else:
                    allowed_max_power[-1] = 0
                    allowed_min_power[-1] = 0

        return allowed_max_power, allowed_min_power


    def calculate_total_flex(self, *, forecast: List[int],
                             p_max_ps: List[int],
                             mpos: List[int],
                             curr_soc: float,
                             final_min_soc: float = 0.0,
                             final_max_soc: float = 1.0,
                             avg_p_bat_of_curr_interval: int,
                             passed_time_of_curr_interval: int,
                             res: int = 15 * 60, t_start: int) \
            -> FlexibilityCalculation:
        """
        Performs all flex calculation steps and stores them in a namedtuple
        :param forecast: the load forecast [W]
        :param p_max_ps: the p_max for peak shaving per interval [W]
        :param curr_soc: the current SoC of the battery [0,1]
        :param final_min_soc: the required min soc at the end [0,1]
        :param final_max_soc: the required max soc at the end [0,1]
        :param avg_p_bat_of_curr_interval: average storage power during the
        current interval until now [W]
        :param passed_time_of_curr_interval: time passed within the current
        interval [s]
        :param res: the resolution to use [s]
        :param t_start: start of the flexibility [Unix Timestamp]
        :return: namedtuple FlexibilityCalculation
        """
        # for debugging only:
        logger.debug(f'Forecast: {forecast[0:int(self.problem_detection_horizon/res)]}')
        logger.debug(f'Multi Purpose Orders: {mpos[0:int(self.problem_detection_horizon/res)]}')
        logger.debug(f'Inputs: p_grid: {p_max_ps}, curr_soc: {curr_soc}, res: {res}')
        #

        if self.PPR_print: print('MPOS: ' + str(mpos))

        # Step 0
        if self.PPR_print:
            print('Step 0')
        start_soc = self.calculate_start_soc_of_current_interval(
            curr_soc=curr_soc,
            avg_p_bat_of_curr_interval=avg_p_bat_of_curr_interval,
            passed_time_of_curr_interval=passed_time_of_curr_interval)

        # critical interval number, first interval without problem detection.
        #  after that there is no problem detection
        critical_interval_number = self.problem_detection_horizon // res
        logger.debug(f'Critical_interval_number: {critical_interval_number}')
        # print(f'Critical Inverval: {self.problem_detection_horizon}')
        # print(f'Critical Inverval Number: {critical_interval_number}')

        problems: List[Problem] = []
        unproblematic_mpos: List[int] = mpos.copy()

        # Only Peak Shaving:
        # Step 1 (a) without MPOs
        if self.PPR_print:
            print('Step 1 (a)')
        # Problems are not given to unit module for now
        available_max_power_no_mpo, available_min_power_no_mpo, _ = \
            self.calculate_available_power_range(
                forecast=forecast,
                p_max_ps=p_max_ps,
                mpos=[0] * len(p_max_ps),
                avg_p_bat_of_curr_interval=avg_p_bat_of_curr_interval,
                res=res,
                passed_time_of_curr_interval=passed_time_of_curr_interval,
                critical_interval=critical_interval_number)
        logger.debug('1(a): Max available power: '+str(available_max_power_no_mpo))
        logger.debug('1(a): Min available power: '+str(available_min_power_no_mpo))

        # Step 2a calculate reachable SoC range
        # Step 2a (a) without MPOs
        if self.PPR_print:
            print('Step 2a (a)')
        # Problems are not given to unit module for now
        reachable_max_soc_no_mpo, reachable_min_soc_no_mpo, \
        extreme_values_no_mpo = \
            self.calculate_soc_flexibility_forward(
                available_max_power=available_max_power_no_mpo,
                available_min_power=available_min_power_no_mpo,
                start_soc=start_soc, res=res,
                critical_interval_max=critical_interval_number,
                critical_interval_min=critical_interval_number,
            )
        logger.debug('2a(a): Max reachable soc: '+str(reachable_max_soc_no_mpo))
        logger.debug('2a(a): Min reachable soc: '+str(reachable_min_soc_no_mpo))
        # get the min and max values within critical interval
        min_max_soc_no_mpo, max_min_soc_no_mpo = extreme_values_no_mpo
        # Check for problem P2.1
        if len(min_max_soc_no_mpo) > 0:
            for interval_no, (problem_interval, min_max_soc) in \
                    enumerate(min_max_soc_no_mpo):
                if self.PPR_print:
                    print('Out 2a (a): min_max < 0 (1): P2.1 at ' + \
                          str(problem_interval) + ' with min_max_soc ' + str(min_max_soc))
                # problem P2.2 too energy intensive peaks are the problem
                # get time of min SoC_max
                min_interval = problem_interval

                # tell about the problem
                # this problem should be only for the unit module
                problems.append(Problem(
                    problem_type='P2.1', interval_no=min_interval,
                    required=int(min_max_soc * 1000),  # soc in [0,1000]
                    realizable=0,
                    negotiation_required=False
                ))
                # check all negative trades before
                for interval_no in range(min_interval, -1, -1):
                    max_soc = reachable_max_soc_no_mpo[interval_no]
                    if max_soc == 1:
                        # trades that come before a time where max_possible == 1
                        # are not relevant anymore
                        break
                    else:
                        max_possible = available_max_power_no_mpo[interval_no]
                        mpo_value = unproblematic_mpos[interval_no]
                    if mpo_value < 0 and max_possible > mpo_value:
                        # it uses physical flexibility
                        if max_possible > 0:
                            # charging would be possible
                            reduction_value = mpo_value
                        else:
                            reduction_value = mpo_value - max_possible
                        unproblematic_mpos[interval_no] -= reduction_value
                        if self.PPR_print:
                            print('Out 2a (a): Problem P2.2 registered.')
                        problems.append(Problem(
                            problem_type='P2.2', interval_no=interval_no,
                            required=mpo_value,
                            realizable=mpo_value - reduction_value,
                            negotiation_required=True
                        ))

            # recalculate 2a without critical interval
            # Step 2a (a) without MPOs
            if self.PPR_print:
                print('re Step 2a (a)')
            reachable_max_soc_no_mpo, reachable_min_soc_no_mpo, \
            _ = self.calculate_soc_flexibility_forward(
                available_max_power=available_max_power_no_mpo,
                available_min_power=available_min_power_no_mpo,
                start_soc=start_soc, res=res,
                critical_interval_max=0,
                critical_interval_min=0
            )
            logger.debug('2a(a)re: Max reachable soc: '+str(reachable_max_soc_no_mpo))
            logger.debug('2a(a)re: Min reachable soc: '+str(reachable_min_soc_no_mpo))

        # Peak Shaving and Trades
        # Step 1 (b) include MPOs
        if self.PPR_print:
            print('Step 1 (b)')

        ## for debugging only:
        # print(f'Forecast: {forecast[0:int(self.problem_detection_horizon/res)]}')
        # print(f'Multi Purpose Orders: {unproblematic_mpos[0:int(self.problem_detection_horizon/res)]}')
        ##

        available_max_power_with_mpo, available_min_power_with_mpo, \
        p1_problems = self.calculate_available_power_range(
            forecast=forecast, p_max_ps=p_max_ps,
            mpos=unproblematic_mpos,
            avg_p_bat_of_curr_interval=avg_p_bat_of_curr_interval,
            res=res,
            passed_time_of_curr_interval=passed_time_of_curr_interval,
            critical_interval=critical_interval_number
        )
        logger.debug('1(b): Max available power: '+str(available_max_power_with_mpo))
        logger.debug('1(b): Min available power: '+str(available_min_power_with_mpo))
        logger.debug('1(b): Problems: '+str(p1_problems))

        # store the open neg requests
        for problem in p1_problems:
            problems.append(problem)
            if problem.problem_type.lower() in ('p1.3', 'p1.2'):
                unproblematic_mpos[problem.interval_no] -= \
                    problem.required - problem.realizable

        # Step 2a (b) with MPOs
        if self.PPR_print:
            print('Step 2a (b)')
        reachable_max_soc_with_mpo, reachable_min_soc_with_mpo, \
        extreme_values_with_mpo = \
            self.calculate_soc_flexibility_forward(
                available_max_power=available_max_power_with_mpo,
                available_min_power=available_min_power_with_mpo,
                start_soc=start_soc, res=res,
                critical_interval_max=critical_interval_number,
                critical_interval_min=critical_interval_number,
            )
        logger.debug('Max: '+str(reachable_max_soc_with_mpo))
        logger.debug('Min: '+str(reachable_min_soc_with_mpo))
        # get the min and max values within critical interval
        min_max_soc_with_mpo, max_min_soc_with_mpo = extreme_values_with_mpo
        logger.debug(min_max_soc_with_mpo)
        logger.debug(max_min_soc_with_mpo)

        # logger.debug('822')
        # Check for problems P2.2 and P2.3
        if len(min_max_soc_with_mpo) > 0 or len(max_min_soc_with_mpo) > 0:
            # Check for Problem P2.3
            for interval_no, (problem_interval, min_max_soc) in \
                    enumerate(min_max_soc_with_mpo):
                if self.PPR_print:
                    print('min_max < 0 (2): P2.2 at ' + \
                          str(problem_interval) + ' with min_max_soc ' + str(min_max_soc))
                # problem P2.2 only discharge trades are the problem
                # get time of min SoC_max
                min_interval = problem_interval
                unallowed_soc_decrease = min_max_soc
                unallowed_trade_power = self.soc_diff_to_power(
                    soc_diff=unallowed_soc_decrease, duration=res)
                # check all negative trades before
                for interval_no in range(min_interval, -1, -1):
                    # reduce all discharging trades that use physical flex
                    mpo_value = unproblematic_mpos[interval_no]
                    if mpo_value < 0:
                        # NOTE (AJ) modified
                        # from: [line 843] possible_without_mpo = available_max_power_no_mpo[interval_no]
                        # changed to: [line 843] possible_without_mpo = available_min_power_no_mpo[interval_no]
                        # Todo: Possible bug in following five lines:
                        possible_without_mpo = available_max_power_no_mpo[interval_no]
                        # reduce trade to bilance flex
                        trade_realizable = min(0, possible_without_mpo)
                        trade_reduction = max(unallowed_trade_power,
                                              mpo_value - trade_realizable)
                        # print('647 trade_reduction', interval_no,
                        #   unallowed_trade_power,
                        # mpo_value - trade_realizable,
                        #   trade_reduction)

                        if trade_reduction < 0:
                            if self.PPR_print:
                                print('Out 2a (b): Problem P2.2 registered.')
                            problems.append(Problem(
                                problem_type='P2.2', interval_no=interval_no,
                                required=mpo_value,
                                realizable=trade_realizable,
                                negotiation_required=True
                            ))
                            unproblematic_mpos[interval_no] = trade_realizable
                            # reduce unallowed trade power until zero
                            unallowed_trade_power -= trade_reduction
                            if unallowed_trade_power >= 0:
                                break

            # Check for Problem P2.3
            # print('865')
            for interval_no, (problem_interval, max_min_soc) in \
                    enumerate(max_min_soc_with_mpo):
                if self.PPR_print:
                    print('max_min < 0 (3): P2.3 at ' + \
                          str(problem_interval) + ' with ' + str(max_min_soc))
                # problem P2.3 only charge trades are the problem
                # get time of max SoC_min
                max_interval = problem_interval
                unallowed_soc_increase = max_min_soc - 1
                unallowed_trade_power = self.soc_diff_to_power(
                    soc_diff=unallowed_soc_increase, duration=res)
                # check all positive trades before
                for interval_no in range(max_interval, -1, -1):
                    # reduce all exceeding charging trades
                    mpo_value = unproblematic_mpos[interval_no]
                    if mpo_value > 0:
                        possible_without_mpo = available_min_power_no_mpo[interval_no]
                        # reduce trade to bilance flex
                        trade_realizable = max(0, possible_without_mpo)
                        trade_reduction = min(unallowed_trade_power,
                                              mpo_value - trade_realizable)
                        if trade_reduction > 0:
                            if self.PPR_print:
                                print('Out 2a (b): Problem P2.3 registered.')
                            problems.append(Problem(
                                problem_type='P2.3', interval_no=interval_no,
                                required=mpo_value,
                                realizable=trade_realizable,
                                negotiation_required=True
                            ))
                            unproblematic_mpos[interval_no] = trade_realizable
                            # reduce unallowed trade power until zero
                            unallowed_trade_power -= trade_reduction
                            if unallowed_trade_power <= 0:
                                break

            # recalculate 1 (b) and 2a (b) without critical intervals
            # recalculate 1 (b)
            available_max_power_with_mpo, available_min_power_with_mpo, _ = \
                self.calculate_available_power_range(
                    forecast=forecast, p_max_ps=p_max_ps,
                    mpos=unproblematic_mpos,
                    avg_p_bat_of_curr_interval=avg_p_bat_of_curr_interval,
                    res=res,
                    passed_time_of_curr_interval=passed_time_of_curr_interval
                )
            # Step 2a (b) with MPOs
            reachable_max_soc_with_mpo, reachable_min_soc_with_mpo, _ = \
                self.calculate_soc_flexibility_forward(
                    available_max_power=available_max_power_with_mpo,
                    available_min_power=available_min_power_with_mpo,
                    start_soc=start_soc, res=res,
                    critical_interval_max=0,
                    critical_interval_min=0,
                )

        # Step 2b calculate required SoC range
        # at this point all problems are detected and stored in problems
        # Step 2b (a) without MPOs
        required_max_soc_no_mpo, required_min_soc_no_mpo = \
            self.calculate_soc_flexibility_backward(
                available_max_power=available_max_power_no_mpo,
                available_min_power=available_min_power_no_mpo,
                final_min_soc=final_min_soc, final_max_soc=final_max_soc,
                res=res
            )
        # Step 2b (b) with MPOs
        required_max_soc_with_mpo, required_min_soc_with_mpo = \
            self.calculate_soc_flexibility_backward(
                available_max_power=available_max_power_with_mpo,
                available_min_power=available_min_power_with_mpo,
                final_min_soc=final_min_soc, final_max_soc=final_max_soc,
                res=res
            )

        # Step 2c combine 2a and 2b to allowed SoC range
        # Step 2c (a) without MPOs
        allowed_max_soc_no_mpo, allowed_min_soc_no_mpo = \
            self.calculate_allowed_soc_range(
                required_max_soc=required_max_soc_no_mpo,
                required_min_soc=required_min_soc_no_mpo,
                reachable_max_soc=reachable_max_soc_no_mpo,
                reachable_min_soc=reachable_min_soc_no_mpo,
                critical_interval=critical_interval_number
            )
        # Step 2c (b) with MPOs
        allowed_max_soc_with_mpo, allowed_min_soc_with_mpo = \
            self.calculate_allowed_soc_range(
                required_max_soc=required_max_soc_with_mpo,
                required_min_soc=required_min_soc_with_mpo,
                reachable_max_soc=reachable_max_soc_with_mpo,
                reachable_min_soc=reachable_min_soc_with_mpo,
                critical_interval=critical_interval_number
            )

        # Step 3 calculate allowed power flexibility
        # Step 3 (a) without mpo

        # print('# 977 Allowed max power')
        # print('wo MPO')
        allowed_max_power_no_mpo, allowed_min_power_no_mpo = \
            self.calculate_allowed_power_flexibility(
                allowed_max_soc=allowed_max_soc_no_mpo,
                allowed_min_soc=allowed_min_soc_no_mpo,
                available_max_power=available_max_power_no_mpo,
                available_min_power=available_min_power_no_mpo,
                res=res, start_soc=start_soc,
                critical_interval=critical_interval_number
            )
        # Step 3 (b) with mpo
        # print('w MPO')
        allowed_max_power_with_mpo, allowed_min_power_with_mpo = \
            self.calculate_allowed_power_flexibility(
                allowed_max_soc=allowed_max_soc_with_mpo,
                allowed_min_soc=allowed_min_soc_with_mpo,
                available_max_power=available_max_power_with_mpo,
                available_min_power=available_min_power_with_mpo,
                res=res, start_soc=start_soc,
                critical_interval=critical_interval_number
            )

        # Step 4 calculate energy flexibility/delta energy
        # increase min_soc to respect discharge efficiency
        # Step 4a (a) without mpo
        # print('# 962 Allowed max power')
        # print('wo MPO')
        allowed_max_incr_soc_no_mpo, allowed_min_incr_soc_no_mpo = \
            self.increase_min_soc_by_discharge_efficiency_losses(
                max_soc=allowed_max_soc_no_mpo,
                min_soc=allowed_min_soc_no_mpo,
                allowed_max_power=allowed_max_power_no_mpo,
                allowed_min_power=allowed_min_power_no_mpo,
                res=res, start_soc=start_soc,
                critical_interval=critical_interval_number, debug_print=False)
        # Step 4a (b) with mpo
        # print('w MPO')
        allowed_max_incr_soc_with_mpo, allowed_min_incr_soc_with_mpo = \
            self.increase_min_soc_by_discharge_efficiency_losses(
                max_soc=allowed_max_soc_with_mpo,
                min_soc=allowed_min_soc_with_mpo,
                allowed_max_power=allowed_max_power_with_mpo,
                allowed_min_power=allowed_min_power_with_mpo,
                res=res, start_soc=start_soc,
                critical_interval=critical_interval_number, debug_print=False)

        # convert to energy flexibility
        # Step 4b (a) without mpo
        allowed_max_energy_delta_no_mpo, allowed_min_energy_delta_no_mpo = \
            self.convert_soc_range_to_energy_flex(
                start_soc=start_soc, max_soc=allowed_max_incr_soc_no_mpo,
                min_soc=allowed_min_incr_soc_no_mpo,
                max_power=allowed_max_power_no_mpo,
                min_power=allowed_min_power_no_mpo)
        # Step 4b (b) with mpo
        allowed_max_energy_delta_with_mpo, allowed_min_energy_delta_with_mpo = \
            self.convert_soc_range_to_energy_flex(
                start_soc=start_soc, max_soc=allowed_max_incr_soc_with_mpo,
                min_soc=allowed_min_incr_soc_with_mpo,
                max_power=allowed_max_power_with_mpo,
                min_power=allowed_min_power_with_mpo)

        # store result in named tuple
        result_no_mpo = Flexibility(
            available_min_power=available_min_power_no_mpo,
            available_max_power=available_max_power_no_mpo,
            required_min_soc=required_min_soc_no_mpo,
            required_max_soc=required_max_soc_no_mpo,
            reachable_min_soc=reachable_min_soc_no_mpo,
            reachable_max_soc=reachable_max_soc_no_mpo,
            allowed_min_soc=allowed_min_soc_no_mpo,
            allowed_max_soc=allowed_max_soc_no_mpo,
            allowed_min_incr_soc=allowed_min_incr_soc_no_mpo,
            allowed_max_incr_soc=allowed_max_incr_soc_no_mpo,
            allowed_max_energy_delta=allowed_max_energy_delta_no_mpo,
            allowed_min_energy_delta=allowed_min_energy_delta_no_mpo,
            allowed_max_power=allowed_max_power_no_mpo,
            allowed_min_power=allowed_min_power_no_mpo,
        )

        result_with_mpo = Flexibility(
            available_min_power=available_min_power_with_mpo,
            available_max_power=available_max_power_with_mpo,
            required_min_soc=required_min_soc_with_mpo,
            required_max_soc=required_max_soc_with_mpo,
            reachable_min_soc=reachable_min_soc_with_mpo,
            reachable_max_soc=reachable_max_soc_with_mpo,
            allowed_min_soc=allowed_min_soc_with_mpo,
            allowed_max_soc=allowed_max_soc_with_mpo,
            allowed_min_incr_soc=allowed_min_incr_soc_with_mpo,
            allowed_max_incr_soc=allowed_max_incr_soc_with_mpo,
            allowed_max_energy_delta=allowed_max_energy_delta_with_mpo,
            allowed_min_energy_delta=allowed_min_energy_delta_with_mpo,
            allowed_max_power=allowed_max_power_with_mpo,
            allowed_min_power=allowed_min_power_with_mpo,
        )
        result = FlexibilityCalculation(
            t_create=0,#int(time.time()),
            t_start=t_start,
            res=res,
            flex_with_mpo=result_with_mpo,
            flex_without_mpo=result_no_mpo,
            problems=problems,
        )
        if self.PPR_print:
            print(f'Probleme: {problems}')

        return result
