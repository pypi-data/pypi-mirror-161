"""A module for non-standard FBA model (e.g. E.coli with RuBisCO)"""
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

from typing import Dict, Iterable

from cobra.core import Metabolite, Reaction, model
from cobra.io import load_model


RBP = Metabolite(
    "rubp__D_c",
    formula="C5H12O11P2",
    name="D-ribulose 1,5-bisphosphate",
    compartment="c",
)
SBP = Metabolite(
    "sbp_c",
    formula="C7H16O13P2",
    name="D-sedoheptulose 1,7-bisphosphate",
    compartment="c",
)
KDPG = Metabolite(
    "2ddg6p_c",
    formula="C6H8O9P",
    name="2-dehydro-3-deoxy-D-gluconate 6-phosphate",
    compartment="c",
)
MALYLCOA = Metabolite(
    "malcoa_c", formula="C25H40N7O20P3S", name="Malyl-CoA", compartment="c"
)
METHANOL = Metabolite("methanol_c", formula="CH4O", name="methanol", compartment="c")
FORMALDEHYDE = Metabolite(
    "formaldehyde_c", formula="CH2O", name="formaldehyde", compartment="c"
)
FORMATE = Metabolite("for_c", formula="CH2O2", name="formate", compartment="c")
R_GLYCERATE = Metabolite(
    "glyc__R_c", formula="C3H5O4", name="(R)-Glycerate", compartment="c"
)
HEX6P = Metabolite(
    "hexulose6p_c", formula="CH4O", name="D-hexulose 6-phosphate", compartment="c"
)


def create_extended_core_model(
    knockins: Iterable[str] = None, carbon_sources: Iterable[str] = None
) -> model:
    """Creates a core model with a few extra `knockin` reactions.

    :param knockins: list of names of reactions to add
    :param carbon_sources: list of potential carbon sources
    :return: a cobra model
    """
    wt_model = load_model("textbook")

    # remove the ATP maintenance requirement. we don't need it for
    # calculating the slope.
    wt_model.reactions.ATPM.lower_bound = 0

    # remove the default carbon source (glucose) so we can choose the ones we
    # want later on
    wt_model.reactions.EX_glc__D_e.lower_bound = 0

    if knockins is not None:
        for ki in knockins:
            add_cytoplasmic_reaction(wt_model, ki, 0, 1000)

    if carbon_sources is not None:
        for cs in carbon_sources:
            add_metabolite_exchange(wt_model, cs)

    return wt_model


def add_reaction(
    model: model,
    rxn_id: str,
    name: str,
    sparse: Dict[str, float],
    lower_bound: float = 0,
    upper_bound: float = 1000,
):
    """
    Adds a new reaction to the model
    """
    reaction = Reaction(
        rxn_id, name=name, lower_bound=lower_bound, upper_bound=upper_bound
    )
    for met_id, coeff in sparse.items():
        try:
            met = model.metabolites.get_by_id(met_id)
        except KeyError:
            raise KeyError(
                f"cannot find the cytoplasmic metabolite {met_id}" f" in the model"
            )
        reaction.add_metabolites({met: coeff})

    model.add_reactions([reaction])


def add_metabolite_exchange(model: model, exchange_met_id: str):
    try:
        met_c = model.metabolites.get_by_id(exchange_met_id + "_c")
    except KeyError:
        raise KeyError("Model does not have a metabolite with ID: " + exchange_met_id)

    met_e = Metabolite(
        exchange_met_id + "_e", met_c.formula, met_c.name, compartment="e"
    )
    model.add_metabolites([met_e])

    rxn_tr = Reaction(
        id=exchange_met_id + "_transport",
        name=met_c.name + " permease",
        lower_bound=-1000,
        upper_bound=1000,
    )
    rxn_tr.add_metabolites({met_c: -1, met_e: 1})
    rxn_ex = Reaction(
        id="EX_" + exchange_met_id + "_e",
        name=met_c.name + " permease",
        lower_bound=0,
        upper_bound=0,
    )
    rxn_ex.add_metabolites({met_e: -1})
    model.add_reactions([rxn_tr, rxn_ex])


def add_cytoplasmic_reaction(
    model: model, rxn_id: str, lower_bound: float = 0, upper_bound: float = 1000
) -> None:

    if rxn_id == "PRK":
        model.add_metabolites([RBP])
        sprs = {"ru5p__D_c": -1, "atp_c": -1, "rubp__D_c": 1, "adp_c": 1}
        add_reaction(
            model, rxn_id, "phosphoribulokinase", sprs, lower_bound, upper_bound
        )
    elif rxn_id == "RBC":
        model.add_metabolites([RBP])
        sprs = {"rubp__D_c": -1, "h2o_c": -1, "co2_c": -1, "3pg_c": 2, "h_c": 3}
        add_reaction(
            model, rxn_id, "RuBisCO carboxylation", sprs, lower_bound, upper_bound
        )
    elif rxn_id == "PRK+RBC":
        model.add_metabolites([RBP])
        sprs = {
            "ru5p__D_c": -1,
            "atp_c": -1,
            "h2o_c": -1,
            "co2_c": -1,
            "3pg_c": 2,
            "h_c": 3,
            "adp_c": 1,
        }
        add_reaction(model, rxn_id, "PRK+RuBisCO", sprs, lower_bound, upper_bound)
    elif rxn_id == "EDD":
        model.add_metabolites([KDPG])
        sprs = {"6pgc_c": -1, "h2o_c": 1, "2ddg6p_c": 1}
        add_reaction(
            model,
            rxn_id,
            "6-phosphogluconate dehydratase",
            sprs,
            lower_bound,
            upper_bound,
        )
    elif rxn_id == "EDA":
        model.add_metabolites([KDPG])
        sprs = {"2ddg6p_c": -1, "g3p_c": 1, "pyr_c": 1}
        add_reaction(
            model,
            rxn_id,
            "2-dehydro-3-deoxy-phosphogluconate aldolase",
            sprs,
            lower_bound,
            upper_bound,
        )
    elif rxn_id == "PKT":
        sprs = {"f6p_c": -1, "pi_c": -1, "e4p_c": 1, "actp_c": 1, "h2o_c": 1}
        add_reaction(model, rxn_id, "phosphoketolase", sprs, lower_bound, upper_bound)
    elif rxn_id == "RED":
        sprs = {"nad_c": -1, "nadh_c": 1}
        add_reaction(model, rxn_id, "free_e", sprs, lower_bound, upper_bound)
    elif rxn_id == "ATP":
        sprs = {"adp_c": -1, "atp_c": 1}
        add_reaction(model, rxn_id, "free_atp", sprs, lower_bound, upper_bound)
    elif rxn_id == "DXS":
        sprs = {"3pg_c": -1, "pyr_c": -1}
        add_reaction(
            model, rxn_id, "deoxyribose synthase", sprs, lower_bound, upper_bound
        )
    elif rxn_id == "MCS":
        model.add_metabolites([MALYLCOA])
        sprs = {
            "mal_L_c": -1,
            "atp_c": -1,
            "coa_c": -1,
            "malcoa_c": 1,
            "adp_c": 1,
            "pi_c": 1,
        }
        add_reaction(
            model, rxn_id, "malyl-CoA synthase", sprs, lower_bound, upper_bound
        )
    elif rxn_id == "MCL":
        model.add_metabolites([MALYLCOA])
        sprs = {"malcoa_c": -1, "accoa_c": 1, "glx_c": 1}
        add_reaction(model, rxn_id, "malyl-CoA lyase", sprs, lower_bound, upper_bound)
    elif rxn_id == "SBP":
        model.add_metabolites([SBP])
        sprs = {"sbp_c": -1, "h2o_c": -1, "s7p_c": 1, "pi_c": 1}
        add_reaction(
            model,
            rxn_id,
            "sedoheptulose bisphosphate phosphatase",
            sprs,
            lower_bound,
            upper_bound,
        )
    elif rxn_id == "SBA":
        model.add_metabolites([SBP])
        sprs = {"sbp_c": 1, "g3p_c": -1, "e4p_c": -1}
        add_reaction(
            model,
            rxn_id,
            "sedoheptulose bisphosphate aldolase",
            sprs,
            lower_bound,
            upper_bound,
        )
    elif rxn_id == "MEDH":
        model.add_metabolites([METHANOL, FORMALDEHYDE])
        sprs = {"methanol_c": -1, "nad_c": -1, "formaldehyde_c": 1, "nadh_c": 1}
        add_reaction(
            model, rxn_id, "methanol dehydrogenase", sprs, lower_bound, upper_bound
        )
    elif rxn_id == "H6PS":
        model.add_metabolites([FORMALDEHYDE, HEX6P])
        sprs = {"ru5p__D_c": -1, "formaldehyde_c": -1, "hexulose6p_c": 1}
        add_reaction(
            model,
            rxn_id,
            "hexulose-6-phosphate synthetase",
            sprs,
            lower_bound,
            upper_bound,
        )
    elif rxn_id == "H6PI":
        model.add_metabolites([HEX6P])
        sprs = {"hexulose6p_c": -1, "f6p_c": 1}
        add_reaction(
            model,
            rxn_id,
            "hexulose-6-phosphate isomerase",
            sprs,
            lower_bound,
            upper_bound,
        )
    elif rxn_id == "H4MPTP":
        model.add_metabolites([FORMALDEHYDE, FORMATE])
        sprs = {"formaldehyde_c": -1, "for_c": 1}
        add_reaction(
            model,
            rxn_id,
            "methylene tetrahydromethanopterin pathway",
            sprs,
            lower_bound,
            upper_bound,
        )
    elif rxn_id == "FDH":
        model.add_metabolites([FORMATE])
        sprs = {"for_c": -1, "nad_c": -1, "co2_c": 1, "nadh_c": 1}
        add_reaction(
            model, rxn_id, "formate dehydrogenase", sprs, lower_bound, upper_bound
        )
    elif rxn_id == "GLYCK":
        model.add_metabolites([R_GLYCERATE])
        sprs = {"glyc__R_c": -1, "atp_c": -1, "adp_c": 1, "3pg_c": 1}
        add_reaction(model, rxn_id, "glycerate kinase", sprs, lower_bound, upper_bound)
    else:
        raise Exception("unknown knockin reaction: " + rxn_id)
