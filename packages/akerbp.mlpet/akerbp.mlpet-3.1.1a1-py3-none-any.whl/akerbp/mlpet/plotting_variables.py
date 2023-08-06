from typing import Any, Dict

import akerbp.mlpet.plotting_helpers as plotting_helpers

# Lithology dict
# Lithology code as key - provides human readable name ['lith'] and color palette['color']
lithology_numbers: Dict[int, Dict[str, str]] = {
    30000: {"lith": "Sandstone", "color": "#ffff00"},
    65000: {"lith": "Shale", "color": "#bebebe"},
    74000: {"lith": "Dolomite", "color": "#8080ff"},
    79000: {"lith": "Limestone/Marl", "color": "#80ffff"},
    70032: {"lith": "Chalk", "color": "#80ffff"},
    88000: {"lith": "Halite", "color": "#7ddfbe"},
    86000: {"lith": "Anhydrite", "color": "#ff80ff"},
    90000: {"lith": "Coal", "color": "black"},
    93000: {"lith": "Basement", "color": "#ef138a"},
}

# Green palette for color in lithology confidence column
# Lithology conf as key - provides color palette['color']
lithology_conf_numbers: Dict[float, Dict[str, str]] = {
    0: {"color": "#ffffff"},
    0.125: {"color": "#ffffff"},
    0.25: {"color": "#e6f2e6"},
    0.375: {"color": "#cce6cc"},
    0.5: {"color": "#b3d9b3"},
    0.625: {"color": "#99cc99"},
    0.75: {"color": "#80c080"},
    0.875: {"color": "#66b366"},
    1.0: {"color": "#008000"},
}


# Basic parameter mapper for input params to the basic well log plots
curve_function_mapper: Dict[str, Dict[Any, Any]] = {
    "AC": {plotting_helpers.add_AC: {"curve_name": "AC"}},
    "RDEP": {
        plotting_helpers.add_RDEP: {
            "curve_name": "RDEP",
        }
    },
    "NEU/DEN": {
        plotting_helpers.add_NEU_DEN: {
            "den_curve_name": "DEN",
            "neu_curve_name": "NEU",
        }
    },
    "GR": {plotting_helpers.add_GR: {"curve_name": "GR"}},
    "MUDGAS": {
        plotting_helpers.add_MUDGAS: {
            "methane_curve_name": "MTHA",
            "ethane_curve_name": "ETHA",
            "propane_curve_name": "PRPA",
        }
    },
    "VSH": {plotting_helpers.add_VSH: {"curve_name": "VSH"}},
    "CALI/BS": {
        plotting_helpers.add_CALI_BS: {
            "cali_curve_name": "CALI",
            "bs_curve_name": "BS",
        }
    },
    "VSH_flag_filter": {
        plotting_helpers.add_VSH_flag_filter: {
            "curve_name": "filter_vsh_cutoff",
        }
    },
    "COAL/CALC flag": {
        plotting_helpers.add_COAL_CALC_flag: {
            "coal_curve_name": "coal_flag",
            "calc_curve_name": "calc_flag",
        }
    },
    "MUD/LOG indicator": {
        plotting_helpers.add_mud_log_indicator: {
            "mud_indicator_curve_name": "mud_indicator",
            "log_indicator_curve_name": "log_indicator",
        }
    },
    "MissedPay prediction": {
        plotting_helpers.add_missedpay_prediction: {
            "prediction_label": "ML Pay Prediction",
            "probability_curve_name": "probabilities",
            "flag_curve_name": "predictions",
        }
    },
    "LITHOLOGY": {  # optional: can send in formation_tops_mapper
        plotting_helpers.add_LITHOLOGY: {
            "lithology_prediction_curve_name": "LITHOLOGY",
            "lithology_confidence_curve_name": "LITHOLOGY_CONF",
            "lithology_numbers": lithology_numbers,
            "lithology_conf_numbers": lithology_conf_numbers,
        }
    },
    "FORMATION": {  # need to specipy ncols, id_column, md_column
        plotting_helpers.add_formations_and_groups: {
            "formation_level": "FORMATION",
            "extend_top_lines": False,
        }
    },
    "GROUP": {  # need to specipy ncols, id_column, md_column
        plotting_helpers.add_formations_and_groups: {
            "formation_level": "GROUP",
            "extend_top_lines": False,
        }
    },
}
