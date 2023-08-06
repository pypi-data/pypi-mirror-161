# The MIT License (MIT)
#
# Copyright (c) 2019 Institute for Molecular Systems Biology, ETH Zurich.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import warnings
from copy import deepcopy
from itertools import combinations, starmap
from multiprocessing import Pool
from typing import Iterable

import numpy as np
import pandas as pd
from cobra.core import model
from optlang.interface import OPTIMAL

from .util import EPSILON


# the solver raises a warning when the model is infeasible, but we don't need
# to print that out
warnings.filterwarnings("ignore", message="solver status is 'infeasible'")


def calculate_slope(
    wt_model: model,
    knockouts: Iterable[str],
    carbon_sources: Iterable[str],
    target_reaction: str,
) -> float:
    """Calculate the slope for a specific combination of KOs and CSs

    :param wt_model: The wild-type model
    :param knockouts: a list of knockouts
    :param carbon_sources: a list of carbon sources (that all are provided
    together)
    :param target_reaction: the target reaction we wish to couple to growth
    :return: the slope (i.e. the ratio of target flux to biomass flux required)
    """

    # we clone the model so we don't change the original object when we knock
    # out stuff
    ko_model = deepcopy(wt_model)

    for ko in knockouts:
        for k in ko.split("|"):
            ko_model.reactions.get_by_id(k).knock_out()

    for cs in carbon_sources:
        ko_model.reactions.get_by_id("EX_" + cs + "_e").lower_bound = -1000

    rxn_target = ko_model.reactions.get_by_id(target_reaction)

    # First, try to see if growth depends on the target at all. If there is
    # growth without it, the slope is 0
    rxn_target.bounds = (0, 0)
    solution = ko_model.optimize()
    if solution.status == OPTIMAL and solution.objective_value > EPSILON:
        return 0.0

    rxn_target.bounds = (1.0 - EPSILON, 1.0 + EPSILON)
    solution = ko_model.optimize()

    # If even with the target reaction on, we still can't find solutions
    # then the slope is undefined
    if solution.status != OPTIMAL or solution.objective_value < EPSILON:
        return np.nan

    slope = 1.0 / solution.objective_value
    return slope


def calculate_slope_multi(
    wt_model: model,
    carbon_sources: Iterable[str],
    single_knockouts: Iterable[str],
    target_reaction: str,
    max_knockouts: int,
    num_processes: int = 1,
    chunksize: int = 10,
) -> pd.DataFrame:
    """Calculates the slope for multiple KO combinations, for a single CS.

    :param wt_model: The wild-type model
    :param carbon_sources: a list of carbon sources (that all are provided
    together)
    :param single_knockouts: a list of single knockouts
    :param target_reaction: the target reaction we wish to couple to growth
    :param max_knockouts: the maximum number of single knockouts to test in
    each combination
    :param num_processes: (default = 1), if set to > 1, uses multiprocessing
    :return: a DataFrame with all the slopes of the knockout combinations
    """
    carbon_sources = tuple(carbon_sources)

    args_list = [
        (wt_model, knockouts, carbon_sources, target_reaction)
        for n_kos in range(max_knockouts + 1)
        for knockouts in combinations(single_knockouts, n_kos)
    ]

    if num_processes > 1:
        with Pool(num_processes) as p:
            slopes = p.starmap(calculate_slope, args_list, chunksize=chunksize)
    else:
        slopes = starmap(calculate_slope, args_list)

    _, ko, cs, _ = zip(*args_list)
    data = zip(ko, cs, slopes)
    return pd.DataFrame(data=data, columns=["knockouts", "carbon_sources", "slope"])
