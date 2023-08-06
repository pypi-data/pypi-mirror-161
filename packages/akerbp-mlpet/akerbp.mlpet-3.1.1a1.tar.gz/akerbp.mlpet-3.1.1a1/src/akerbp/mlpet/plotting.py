import json
from typing import Any, Dict, List, Tuple

import pandas as pd
import plotly.graph_objects as go

import akerbp.mlpet.data.mappings as default_mappings
import akerbp.mlpet.plotting_helpers as plotting_helpers
import akerbp.mlpet.plotting_variables as plotting_variables
import akerbp.mlpet.utilities as utilities

curve_function_mapper = plotting_variables.curve_function_mapper
lithology_conf_numbers = plotting_variables.lithology_conf_numbers
lithology_numbers = plotting_variables.lithology_numbers


def plot_default_well_profile(
    well_name: str,
    df: pd.DataFrame,
    md_column: str,
    id_column: str = None,
    extend_formation_top_lines: bool = False,
    extend_group_top_lines: bool = False,
    lithology_numbers: Dict[int, Dict[str, Any]] = lithology_numbers,
    lithology_conf_numbers: Dict[float, Dict[str, Any]] = lithology_conf_numbers,
    figsize: Tuple[int, int] = (1500, 1000),
    show_fig: bool = False,
    **kwargs,
) -> go.Figure:
    """
    Wrapper function to create basic well log plot.

    NOTE: If plotting NEU and DEN, they are to be plotted together under feature_to_plot argument "NEU/DEN". Therefore, both columns has to exist in df, but could be nan.
    NOTE: If plotting CALI and BS, they are to be plotted together under feature_to_plot argument "CALI/BS". Therefore, both columns has to exist in df, but could be nan.

    Possible features_to_plot input that has a template plotting function:
        - "MUDGAS"
        - "AC"
        - "NEU/DEN"
        - "GR"
        - "VSH"
        - "RDEP"
        - "CALI/BS"
        - "COAL/CALC flag"
        - "MUD/LOG indicator"
        - "MissedPay prediction"
        - "LITHOLOGY"
        - "FORMATION"
        - "GROUP"

    Args:
        well_name (str): wellbore name
        df (pd.DataFrame): dataframe with all data to be plotted
        id_column (str): name of well name column in df
        md_column (str): name of depth column in df
        features_to_plot (List[str], optional): list of features to plot. If a predefined plotting routine isn't availabe for the provided column,
            it will be plotted with the default routine. To plot lithology, add "LITHOLOGY" in features_to_plot. Defaults to [ "AC", "NEU/DEN", "RDEP", "CALI/BS", "GR", "FORMATION", "GROUP", ].
        extend_formation_top_lines (bool, optional): Whether to exted the formation top lines across all subplots. Defaults to False.
        extend_group_top_lines (bool, optional): Whether to exted the group top lines across all subplots. Defaults to False.
        lithology_numbers (Dict[int, Dict[str, Any]]): dictionary with lithology numbers as key with human readable name['lith'] and color['color'] for plot as value. Defaults to lithology_numbers Dict in akerbp.mlpet.plotting_variables.py.
        lithology_conf_numbers (Dict[float, Dict[str, Any]]): dictionary with lithology conf numbers as key with color for plot as value['color']. Defaults to lithology_conf_numbers Dict in akerbp.mlpet.plotting_variables.py.
        figsize (Tuple[int, int], optional): figure size (W x H) in pixels. Defaults to (1500, 1000).
        show_fig (bool, optional): Wheter to save fig. If False the figure will be returned by the function. Defaults to False.

    Returns:
        go.Figure: plotly graph_object Figure
    """

    features_to_plot: List[str] = kwargs.get(
        "features_to_plot",
        [
            "AC",
            "NEU/DEN",
            "RDEP",
            "CALI/BS",
            "GR",
            "FORMATION",
            "GROUP",
        ],
    )
    df = df.sort_values(md_column)

    # Map curve names in the provided dataframe
    df = utilities.standardize_curve_names(
        df=df, mapper=default_mappings.base_mappings["curve_mappings"]
    )

    if id_column is not None:
        id_column = default_mappings.base_mappings["curve_mappings"][id_column]
        df = df[df[id_column] == well_name]

    ncols = len(features_to_plot)

    if "FORMATION" in features_to_plot or "GROUP" in features_to_plot:
        if id_column is None:
            raise ValueError(
                "Cannot add FORMATION/GROUP to plottview because id_column is not provided."
            )
        else:
            # NOTE: Need to specify ncols, id_columm and md_column in order to add FORMATION to subplot
            # Can specify whether to extend top lines across all subplots
            curve_function_mapper["FORMATION"] = {
                plotting_helpers.add_formations_and_groups: {
                    "ncols": ncols,
                    "id_column": id_column,
                    "formation_level": "FORMATION",
                    "extend_top_lines": extend_formation_top_lines,
                }
            }
            # NOTE: Need to specify ncols, id_columm and md_column in order to add GROUP to subplot
            # Can specify whether to extend top lines across all subplots
            curve_function_mapper["GROUP"] = {
                plotting_helpers.add_formations_and_groups: {
                    "ncols": ncols,
                    "id_column": id_column,
                    "formation_level": "GROUP",
                    "extend_top_lines": extend_group_top_lines,
                }
            }

    # NOTE: Optional - Can redefine lithology_numbers and lithology_conf_numbers from input params
    if "LITHOLOGY" in features_to_plot:
        curve_function_mapper["LITHOLOGY"] = {
            plotting_helpers.add_LITHOLOGY: {
                "lithology_prediction_curve_name": "LITHOLOGY",
                "lithology_confidence_curve_name": "LITHOLOGY_CONF",
                "lithology_numbers": lithology_numbers,
                "lithology_conf_numbers": lithology_conf_numbers,
            }
        }

    fig = plotting_helpers.initialize_figure(
        well_name=well_name,
        depth_values=df[md_column],
        ncols=ncols,
        figsize=figsize,
    )

    for i_curve, curve_name in enumerate(features_to_plot):
        # Map curve name in a standard name convension is specified in mappingsfile
        if curve_name in default_mappings.base_mappings["curve_mappings"].keys():
            curve_name = default_mappings.base_mappings["curve_mappings"][curve_name]

        # Plot each curve
        if curve_name in curve_function_mapper.keys():
            for function, parameters in curve_function_mapper[curve_name].items():
                fig = function(
                    fig=fig,
                    i_curve=i_curve + 1,
                    df=df,
                    md_column=md_column,
                    **parameters,
                )
        else:
            fig = plotting_helpers.add_curve(
                fig=fig,
                i_curve=i_curve + 1,
                df=df,
                curve_name=curve_name,
                md_column=md_column,
            )

    if show_fig:
        fig.show()
    return fig


def plot_well_profile_missedpay(
    well_name: str,
    df_input: pd.DataFrame,
    df_result: pd.DataFrame,
    id_column: str,
    md_column: str,
    extend_formation_top_lines: bool = False,
    extend_group_top_lines: bool = True,
    lithology_numbers: Dict[int, Dict[str, Any]] = lithology_numbers,
    lithology_conf_numbers: Dict[float, Dict[str, Any]] = lithology_conf_numbers,
    figsize: Tuple[int, int] = (1500, 1000),
    show_fig: bool = False,
    **kwargs,
) -> go.Figure:
    """
    Wrapper function to plot well profile plot for Missed pay prediction

    NOTE: If plotting NEU and DEN, they are to be plotted together under feature_to_plot argument "NEU/DEN". Therefore, both columns has to exist in df, but could be nan.
    NOTE: If plotting CALI and BS, they are to be plotted together under feature_to_plot argument "CALI/BS". Therefore, both columns has to exist in df, but could be nan.

    Possible features_to_plot input that has a template plotting function:
        - "MUDGAS"
        - "AC"
        - "NEU/DEN"
        - "GR"
        - "VSH"
        - "RDEP"
        - "CALI/BS"
        - "COAL/CALC flag"
        - "MUD/LOG indicator"
        - "MissedPay prediction"
        - "LITHOLOGY"
        - "FORMATION"
        - "GROUP"

    Args:
        well_name (str): wellbore name
        df_input (pd.DataFrame): dataframe with colums to plot. The data in this dataframe is raw.
        df_result (pd.DataFrame): dataframe wiht column to plot. The data in this dataframe is preprocessed.
        id_column (str): name of well name column in df
        md_column (str): name of depth column in df
        features_to_plot (List[str], optional): list of features to plot. Defaults to [ "MUDGAS", "AC", "NEU/DEN", "GR", "VSH", "RDEP", "CALI/BS", "COAL/CALC_flag", "MUD/LOG_indicator", "MissedPay prediction", "LITHOLOGY", "FORMATION", "GROUP"].
        extend_formation_top_lines (bool, optional): Whether to exted the formation top lines across all subplots. Defaults to False.
        extend_group_top_lines (bool, optional): Whether to exted the group top lines across all subplots. Defaults to False.
        lithology_numbers (Dict[int, Dict[str, Any]]): dictionary with lithology numbers as key with human readable name['lith'] and color['color'] for plot as value. Defaults to lithology_numbers Dict in akerbp.mlpet.plotting_variables.py.
        lithology_conf_numbers (Dict[float, Dict[str, Any]]): dictionary with lithology conf numbers as key with color for plot as value['color']. Defaults to lithology_conf_numbers Dict in akerbp.mlpet.plotting_variables.py.
        figsize (Tuple[int, int], optional): figure size (W x H) in pixels. Defaults to (1500, 1000).
        show_fig (bool, optional): Wheter to save fig. If False the figure will be returned by the function. Defaults to False.

    Returns:
        go.Figure: plotly graph_object Figure
    """

    features_to_plot: List[str] = kwargs.get(
        "features_to_plot",
        [
            "MUDGAS",
            "AC",
            "NEU/DEN",
            "GR",
            "VSH",
            "RDEP",
            "CALI/BS",
            "COAL/CALC flag",
            "MUD/LOG indicator",
            "MissedPay prediction",
            "LITHOLOGY",
            "FORMATION",
            "GROUP",
        ],
    )

    df_input = df_input[df_input[id_column] == well_name].sort_values(md_column)
    df_result = df_result[df_result[id_column] == well_name].sort_values(md_column)

    # Map curve names in the provided dataframe
    df_input = utilities.standardize_curve_names(
        df=df_input, mapper=default_mappings.base_mappings["curve_mappings"]
    )
    df_result = utilities.standardize_curve_names(
        df=df_result, mapper=default_mappings.base_mappings["curve_mappings"]
    )
    id_column = default_mappings.base_mappings["curve_mappings"][id_column]

    ncols = len(features_to_plot)

    # Get formation tops mapper
    try:
        client = utilities.get_cognite_client()
        # Load from CDF
        formation_tops_mapper = utilities.get_formation_tops([well_name], client)
    except Exception:
        try:
            # Load from file when missing in CDF
            with open(
                "data/formation_tops/"
                + well_name.replace("/", "_")
                + "_formation_tops_mapper.txt"
            ) as f:
                data = f.read()
                formation_tops_mapper = json.loads(data)[well_name]
        except Exception:
            # could not find formation tops
            formation_tops_mapper = {}

    # Redefine curve parameter mapper for missed pay since input in spittet across to different datasets
    curve_function_mapper: Dict[str, Dict[Any, Any]] = {
        "AC": {
            plotting_helpers.add_AC: {
                "df": df_input,
                "curve_name": "AC",
                "md_column": md_column,
            }
        },
        "RDEP": {
            plotting_helpers.add_RDEP: {
                "df": df_input,
                "curve_name": "RDEP",
                "md_column": md_column,
            }
        },
        "NEU/DEN": {
            plotting_helpers.add_NEU_DEN: {
                "df": df_input,
                "den_curve_name": "DEN",
                "neu_curve_name": "NEU",
                "md_column": md_column,
            }
        },
        "GR": {
            plotting_helpers.add_GR: {
                "df": df_input,
                "curve_name": "GR",
                "md_column": md_column,
            }
        },
        "MUDGAS": {
            plotting_helpers.add_MUDGAS: {
                "df": df_input,
                "methane_curve_name": "MTHA",
                "ethane_curve_name": "ETHA",
                "propane_curve_name": "PRPA",
                "md_column": md_column,
            }
        },
        "VSH": {
            plotting_helpers.add_VSH: {
                "df": df_result,
                "curve_name": "VSH",
                "md_column": md_column,
            }
        },
        "CALI/BS": {
            plotting_helpers.add_CALI_BS: {
                "df": df_input,
                "cali_curve_name": "CALI",
                "bs_curve_name": "BS",
                "md_column": md_column,
            }
        },
        "VSH_flag_filter": {
            plotting_helpers.add_VSH_flag_filter: {
                "df": df_result,
                "curve_name": "filter_vsh_cutoff",
                "md_column": md_column,
            }
        },
        "COAL/CALC flag": {
            plotting_helpers.add_COAL_CALC_flag: {
                "df": df_result,
                "coal_curve_name": "coal_flag",
                "calc_curve_name": "calc_flag",
                "md_column": md_column,
            }
        },
        "MUD/LOG indicator": {
            plotting_helpers.add_mud_log_indicator: {
                "df": df_result,
                "mud_indicator_curve_name": "mud_indicator",
                "log_indicator_curve_name": "log_indicator",
                "md_column": md_column,
            }
        },
        "MissedPay prediction": {
            plotting_helpers.add_missedpay_prediction: {
                "df": df_result,
                "prediction_label": "ML Pay Prediction",
                "probability_curve_name": "probabilities",
                "flag_curve_name": "predictions",
                "md_column": md_column,
            }
        },
        "LITHOLOGY": {
            plotting_helpers.add_LITHOLOGY: {
                "df": df_result,
                "lithology_prediction_curve_name": "LITHOLOGY",
                "lithology_confidence_curve_name": "LITHOLOGY_CONF",
                "md_column": md_column,
                "lithology_numbers": lithology_numbers,
                "lithology_conf_numbers": lithology_conf_numbers,
            }
        },
        "FORMATION": {
            plotting_helpers.add_formations_and_groups: {
                "df": df_input,
                "ncols": ncols,
                "id_column": id_column,
                "md_column": md_column,
                "formation_level": "FORMATION",
                "formation_tops_mapper": formation_tops_mapper,
                "extend_top_lines": extend_formation_top_lines,
            }
        },
        "GROUP": {
            plotting_helpers.add_formations_and_groups: {
                "df": df_input,
                "ncols": ncols,
                "id_column": id_column,
                "md_column": md_column,
                "formation_level": "GROUP",
                "formation_tops_mapper": formation_tops_mapper,
                "extend_top_lines": extend_group_top_lines,
            }
        },
    }

    fig = plotting_helpers.initialize_figure(
        well_name=well_name,
        depth_values=df_input[md_column],
        ncols=ncols,
        figsize=figsize,
    )

    for i_curve, curve_name in enumerate(features_to_plot):
        # Map curve name in a standard name convension is specified in mappingsfile
        if curve_name in default_mappings.base_mappings["curve_mappings"].keys():
            curve_name = default_mappings.base_mappings["curve_mappings"][curve_name]

        # Plot each curve
        if curve_name in curve_function_mapper.keys():
            for function, parameters in curve_function_mapper[curve_name].items():
                fig = function(fig=fig, i_curve=i_curve + 1, **parameters)
        else:
            try:
                fig = plotting_helpers.add_curve(
                    fig=fig,
                    i_curve=i_curve + 1,
                    df=df_input,
                    curve_name=curve_name,
                    md_column=md_column,
                )
            except Exception:
                fig = plotting_helpers.add_curve(
                    fig=fig,
                    i_curve=i_curve + 1,
                    df=df_result,
                    curve_name=curve_name,
                    md_column=md_column,
                )
                pass

    if show_fig:
        fig.show()

    return fig
