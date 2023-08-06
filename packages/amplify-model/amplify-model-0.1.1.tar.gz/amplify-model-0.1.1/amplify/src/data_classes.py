from typing import List, NamedTuple


class Flexibility (NamedTuple):
    available_max_power: List[int]
    available_min_power: List[int]
    required_max_soc: List[float]
    required_min_soc: List[float]
    reachable_max_soc: List[float]
    reachable_min_soc: List[float]
    allowed_max_soc: List[float]
    allowed_min_soc: List[float]
    allowed_max_incr_soc: List[float]
    allowed_min_incr_soc: List[float]
    allowed_max_energy_delta: List[int]
    allowed_min_energy_delta: List[int]
    allowed_max_power: List[int]
    allowed_min_power: List[int]


class Problem(NamedTuple):
    """
    This class holds all information about detected problems
    """
    problem_type: str
    negotiation_required: bool
    required: int  # if negotiation_required: trade value [W]
    realizable: int # if negotiation_required: possible load [W]
    interval_no: int  # interval number


class FlexibilityCalculation(NamedTuple):
    """
    This class simply holds all the relevant information of a flex calculation
    """
    flex_without_mpo: Flexibility
    flex_with_mpo: Flexibility
    t_create: int
    t_start: int
    res: int
    problems: List[Problem]
