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

from itertools import combinations

import numpy as np
import pandas as pd


EPSILON = 1e-4

################################################################################
#                          HTML output tools                                   #
################################################################################


def model_summary(model, solution, html):
    reaction2flux_dict = dict(
        [(model.reactions[i], solution.x[i]) for i in range(len(model.reactions))]
    )

    display_exchange_reactions(model, reaction2flux_dict, html)

    for m in model.metabolites:
        display_metabolite_reactions(model, m, reaction2flux_dict, html)


def display_exchange_reactions(model, reaction2flux_dict, html):
    # metabolite
    html.write("<br />\n")
    html.write('<a name="EXCHANGE"></a>\n')
    html.write("Exchange reactions: <br />\n")
    html.write("<br />\n")

    titles = [
        "Sub System",
        "Reaction Name",
        "Reaction ID",
        "Reaction",
        "LB",
        "UB",
        "Reaction Flux",
    ]

    # fluxes
    rowdicts = []
    for r in model.reactions:
        if r.subsystem not in ["", "Exchange"]:
            continue
        if abs(reaction2flux_dict[r]) < 1e-10:
            continue

        direction = np.sign(reaction2flux_dict[r])
        d = {
            "Sub System": "Exchange",
            "Reaction Name": r.name,
            "Reaction ID": r.id,
            "Reaction": display_reaction(r, None, direction),
            "LB": "%g" % r.lower_bound,
            "UB": "%g" % r.upper_bound,
            "Reaction Flux": "%.2g" % abs(reaction2flux_dict[r]),
            "sortkey": reaction2flux_dict[r],
        }

        rowdicts.append(d)

    # add a zero row (separating forward and backward) and sort the
    # rows according to the net flux
    rowdicts.append({"sortkey": 0})
    rowdicts.sort(key=lambda x: x["sortkey"])

    # add color to the rows
    max_flux = max([abs(d["sortkey"]) for d in rowdicts])
    rowcolors = [color_gradient(d["sortkey"] / max_flux) for d in rowdicts]

    html.write_table(rowdicts, titles, rowcolors=rowcolors)


def display_metabolite_reactions(model, m, reaction2flux_dict, html):
    # metabolite
    html.write("<br />\n")
    html.write('<a name="%s"></a>\n' % m.id)
    html.write("Metabolite name: " + m.name + "<br />\n")
    html.write("Metabolite ID: " + m.id + "<br />\n")
    html.write("Compartment: " + m.compartment + "<br />\n")
    html.write("<br />\n")

    titles = [
        "Sub System",
        "Reaction Name",
        "Reaction ID",
        "Reaction",
        "LB",
        "UB",
        "Reaction Flux",
        "Net Flux",
    ]

    # fluxes
    rowdicts = []
    for r in m.get_reaction():
        if abs(reaction2flux_dict[r]) < 1e-10:
            continue

        direction = np.sign(reaction2flux_dict[r])
        net_flux = reaction2flux_dict[r] * r.get_coefficient(m)
        d = {
            "Sub System": r.subsystem,
            "Reaction Name": r.name,
            "Reaction ID": r.id,
            "Reaction": display_reaction(r, m, direction),
            "LB": "%g" % r.lower_bound,
            "UB": "%g" % r.upper_bound,
            "Reaction Flux": "%.2g" % abs(reaction2flux_dict[r]),
            "Net Flux": "%.2g" % net_flux,
            "sortkey": -net_flux,
        }

        rowdicts.append(d)

    if rowdicts == []:
        return

    # add a zero row (separating forward and backward) and sort the
    # rows according to the net flux
    rowdicts.append({"sortkey": 0})
    rowdicts.sort(key=lambda x: x["sortkey"])

    # add color to the rows
    max_flux = max([abs(d["sortkey"]) for d in rowdicts])
    rowcolors = [color_gradient(d["sortkey"] / max_flux) for d in rowdicts]

    html.write_table(rowdicts, titles, rowcolors=rowcolors)


def display_reaction(r, m_bold=None, direction=1):
    """
    Returns a string representation of a reaction and highlights the
    metabolite 'm' using HTML tags.
    """
    s_left = []
    s_right = []
    for m in r.get_reactants() + r.get_products():
        if m == m_bold:
            s_met = f"<a href='#{m.id}'><b>{m.id}</b></a>"
        else:
            s_met = f"<a href='#{m.id}'>{m.id}</a>"

        coeff = r.get_coefficient(m)
        if abs(coeff) == 1:
            s_coeff = ""
        else:
            s_coeff = f"{abs(coeff):g} "

        if coeff < 0:
            s_left += [s_coeff + s_met]
        else:
            s_right += [s_coeff + s_met]

    if direction == 1:
        return " + ".join(s_left) + " &#8651; " + " + ".join(s_right)
    else:
        return " + ".join(s_right) + " &#8651; " + " + ".join(s_left)


def color_gradient(x):
    """
    Returns a color in Hex-RGB format between white and red if x is positive
    or between white and green if x is negative
    """
    grad = 220 - abs(x) * 80
    if x > 0:
        return "%.2x%.2x%.2x" % (255, grad, grad)
    elif x < 0:
        return "%.2x%.2x%.2x" % (grad, 255, grad)
    else:
        return "%.2x%.2x%.2x" % (100, 100, 100)


def filter_redundant_knockouts(result_df: pd.DataFrame):
    """Rearranges and filters results from calculate_slope_multi

    :param df: The DataFrame result from calculate_slope_multi()
    :return: A pivot table of all relevant knockouts vs carbon_sources.
    """
    df = result_df.pivot("carbon_sources", "knockouts", "slope")

    # only keep columns (knockouts) with at least one positive slope
    df = df.loc[:, (df > EPSILON).any(axis=0)]

    redundant_kos = set()
    smallest_slopes = []
    highest_slopes = []

    for ko_set in df.columns:
        # iterate through all the subsets to see if there is one with the
        # same yield and slope
        smallest_slopes.append(df[ko_set][df[ko_set] > 0].min())
        highest_slopes.append(df[ko_set].max())

        for ko_subset in [
            tuple(subset)
            for n_kos in range(len(ko_set))
            for subset in combinations(ko_set, n_kos)
        ]:
            if ko_subset not in df.columns:
                continue
            if (df[ko_subset] == df[ko_set]).all(axis=0):
                redundant_kos.add(ko_set)
                break

    # add another row for the smallest non-zero slope achieved by each KO
    df = df.transpose()
    df["smallest_slope"] = smallest_slopes
    df["highest_slope"] = highest_slopes
    df["slope_ratio"] = df["highest_slope"] / df["smallest_slope"]
    df["no_knockouts"] = df.index.map(len)

    df.drop(redundant_kos, axis=0, inplace=True)

    return df.sort_values(["smallest_slope", "no_knockouts"])
