# The MIT License (MIT)
#
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich.
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

from copy import deepcopy
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cobra.core import model
from cobra.flux_analysis import pfba, phenotype_phase_plane
from optlang.interface import OPTIMAL


def production_envelope(
    wt_model: model,
    knockouts: Iterable[str],
    carbon_sources: Iterable[str],
    target_reaction: str,
) -> pd.DataFrame:
    """Calculates the data of the production envelope for a KO.

    :param wt_model: the Wild-Type model without any knockouts
    :param knockouts: the list of KOs
    :param carbon_sources: the list of carbon sources
    :param target_reaction: the reaction to place on the x-axis of the PPP
    :return: A DataFrame with the biomass yield ranges for each x-value
    """
    ko_model = deepcopy(wt_model)
    for ko in knockouts:
        for k in ko.split("|"):
            ko_model.reactions.get_by_id(k).knock_out()
    for cs in carbon_sources:
        ko_model.reactions.get_by_id("EX_" + cs + "_e").lower_bound = -1000
    return phenotype_phase_plane.production_envelope(ko_model, target_reaction)


def plot_production_envelope(
    wt_model: model,
    knockouts: Iterable[str],
    carbon_sources: Iterable[str],
    target_reaction: str,
) -> plt.Figure:
    prod_env_df = production_envelope(
        wt_model=wt_model,
        knockouts=knockouts,
        carbon_sources=carbon_sources,
        target_reaction=target_reaction,
    )

    fig, ax = plt.subplots(1, 1)
    ax.plot(prod_env_df[target_reaction], prod_env_df.flux_minimum, "b-")
    ax.plot(prod_env_df[target_reaction], prod_env_df.flux_maximum, "b-")

    ax.fill_between(
        prod_env_df[target_reaction],
        prod_env_df.flux_minimum,
        prod_env_df.flux_maximum,
        linewidth=0,
        alpha=0.1,
        facecolor="blue",
    )

    ax.set_xlabel(f"rate of {target_reaction}")
    ax.set_ylabel(f"biomass rate")

    return fig


def plot_flux(
    wt_model: model,
    knockouts: Iterable[str],
    carbon_sources: Iterable[str],
    target_reaction: str,
) -> "Builder":
    """Plot the flux solution (pFBA) for the model with the target reaction.

    To plot the flux map inside a Jupyter notebook, use
    `b.display_in_notebook(js_source='web')`

    To plot the flux map in your browser, use `b.display_in_browser()`

    :param wt_model: The wild-type model
    :param knockouts: a list of knockouts
    :param carbon_sources: a list of carbon sources (that all are provided
    together)
    :param target_reaction: the target reaction we wish to couple to growth
    :return: an Escher Builder object
    """
    from escher import Builder

    # we clone the model so we don't change the original object when we knock
    # out stuff
    ko_model = deepcopy(wt_model)

    for ko in knockouts:
        for k in ko.split("|"):
            ko_model.reactions.get_by_id(k).knock_out()

    for cs in carbon_sources:
        ko_model.reactions.get_by_id("EX_" + cs + "_e").lower_bound = -1000

    rxn_target = ko_model.reactions.get_by_id(target_reaction)
    rxn_target.lower_bound = 1.0 - 1e-6
    rxn_target.upper_bound = 1.0 + 1e-6
    solution = ko_model.optimize()

    if solution.status != OPTIMAL or solution.objective_value < 1e-6:
        raise ValueError(
            f"The model is infeasible when the flux in "
            f"{target_reaction} is set to 1"
        )

    pfba_solution = pfba(ko_model)
    flux_df = pfba_solution.fluxes
    flux_df[np.abs(flux_df) < 1e-5] = 0
    flux_dict = flux_df.to_dict()
    flux_dict["BIOMASS_Ecoli_core_w_GAM"] = 1.0

    b = Builder(map_name="e_coli_core.Core metabolism", reaction_data=flux_dict)
    return b
