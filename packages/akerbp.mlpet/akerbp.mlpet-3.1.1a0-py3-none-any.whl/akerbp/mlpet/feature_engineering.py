import warnings
from collections import defaultdict
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd
from cognite.client import CogniteClient
from scipy.interpolate import interp1d

import akerbp.mlpet.petrophysical_features as petro
import akerbp.mlpet.utilities as utilities


def add_log_features(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    """
    Creates columns with log10 of curves. All created columns are suffixed with
    '_log'. All negative values are set to zero and 1 is added to all values. In
    other words, this function is synonymous of numpy's log1p.

    Args:
        df (pd.DataFrame): dataframe with columns to calculate log10 from

    Keyword Args:
        log_features (list, optional): list of column names for the columns that should be
            loggified. Defaults to None

    Returns:
        pd.DataFrame: New dataframe with calculated log columns
    """
    log_features: List[str] = kwargs.get("log_features", None)
    if log_features is not None:
        log_cols = [col + "_log" for col in log_features]
        df[log_cols] = np.log10(df[log_features].clip(lower=0) + 1)
    return df


def add_gradient_features(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    """
    Creates columns with gradient of curves. All created columns are suffixed with
    '_gradient'.

    Args:
        df (pd.DataFrame): dataframe with columns to calculate gradient from
    Keyword Args:
        gradient_features (list, optional): list of column names for the columns
            that gradient features should be calculated for. Defaults to None.

    Returns:
        pd.DataFrame: New dataframe with calculated gradient feature columns
    """
    gradient_features: List[str] = kwargs.get("gradient_features", None)
    if gradient_features is not None:
        gradient_cols = [col + "_gradient" for col in gradient_features]
        for i, feature in enumerate(gradient_features):
            df[gradient_cols[i]] = np.gradient(df[feature])
    return df


def add_rolling_features(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    """
    Creates columns with window/rolling features of curves. All created columns
    are suffixed with '_window_mean' / '_window_max' / '_window_min'.

    Args:
        df (pd.DataFrame): dataframe with columns to calculate rolling features from

    Keyword Args:
        rolling_features (list): columns to apply rolling features to. Defaults to None.
        depth_column (str): The name of the column to use to determine the sampling
            rate. Without this kwarg no rolling features are calculated.
        window (float): The window size to use for calculating the rolling
            features. **The window size is defined in distance**! The sampling rate
            is determined from the depth_column kwarg and used to transform the window
            size into an index based window. If this is not provided, no rolling features are calculated.

    Returns:
        pd.DataFrame: New dataframe with calculated rolling feature columns
    """
    rolling_features: List[str] = kwargs.get("rolling_features", None)
    window = kwargs.get("window", None)
    depth_column = kwargs.get("depth_column", None)
    if rolling_features is not None and window is not None and depth_column is not None:
        sampling_rate = utilities.calculate_sampling_rate(df[depth_column])
        window_size = int(window / sampling_rate)
        mean_cols = [col + "_window_mean" for col in rolling_features]
        df[mean_cols] = (
            df[rolling_features]
            .rolling(center=False, window=window_size, min_periods=1)
            .mean()
        )
        min_cols = [col + "_window_min" for col in rolling_features]
        df[min_cols] = (
            df[rolling_features]
            .rolling(center=False, window=window_size, min_periods=1)
            .min()
        )
        max_cols = [col + "_window_max" for col in rolling_features]
        df[max_cols] = (
            df[rolling_features]
            .rolling(center=False, window=window_size, min_periods=1)
            .max()
        )
    return df


def add_sequential_features(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Adds n past values of columns (for sequential models modelling). All created
    columns are suffixed with '_1' / '_2' / ... / '_n'.

    Args:
        df (pd.DataFrame): dataframe to add time features to

    Keyword Args:
        sequential_features (list, optional): columns to apply shifting to. Defaults to None.
        shift_size (int, optional): Size of the shifts to calculate. In other words, number of past values
            to include. If this is not provided, no sequential features are calculated.

    Returns:
        pd.DataFrame: New dataframe with sequential gradient columns
    """
    sequential_features: List[str] = kwargs.get("sequential_features", None)
    shift_size: int = kwargs.get("shift_size", None)
    if sequential_features and shift_size is not None:
        for shift in range(1, shift_size + 1):
            sequential_cols = [f"{c}_{shift}" for c in sequential_features]
            df[sequential_cols] = df[sequential_features].shift(periods=shift)
    return df


def add_petrophysical_features(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Creates petrophysical features according to relevant heuristics/formulas.

    The features created are as follows (each one can be toggled on/off via the
    'petrophysical_features' kwarg)::

        - VPVS = ACS / AC
        - PR = (VP ** 2 * 2 * VS ** 2) / (2 * (VP ** 2 * VS ** 2)) where
        - VP = 304.8 / AC
        - VS = 304.8 / ACS
        - RAVG = AVG(RDEP, RMED, RSHA), if at least two of those are present
        - LFI = 2.95 * ((NEU + 0.15) / 0.6) * DEN, and
            - LFI < *0.9 = 0
            - NaNs are filled with 0
        - FI = (ABS(LFI) + LFI) / 2
        - LI = ABS(ABS(LFI) * LFI) / 2
        - AI = DEN * ((304.8 / AC) ** 2)
        - CALI*BS = CALI * BS, where
            - BS is calculated using the guess_BS_from_CALI function from this
            module it is not found in the pass dataframe
        - VSH = Refer to the calculate_VSH docstring for more info on this

    Args:
        df (pd.DataFrame): dataframe to which add features from and to

    Keyword Args:
        petrophysical_features (list): A list of all the petrophysical features
            that should be created (see above for all the potential features
            this method can create). This defaults to an empty list (i.e. no
            features created).

    Returns:
        pd.DataFrame: dataframe with added features
    """
    petrophysical_features: List[str] = kwargs.get("petrophysical_features", None)

    if petrophysical_features is not None:
        # Calculate relevant features
        if "VP" in petrophysical_features:
            df = petro.calculate_VP(df, **kwargs)

        if "VS" in petrophysical_features:
            df = petro.calculate_VS(df, **kwargs)

        if "VPVS" in petrophysical_features:
            df = petro.calculate_VPVS(df)

        if "PR" in petrophysical_features:
            df = petro.calculate_PR(df)

        if "RAVG" in petrophysical_features:
            df = petro.calculate_RAVG(df)

        if "LFI" in petrophysical_features:
            df = petro.calculate_LFI(df, **kwargs)

        if "FI" in petrophysical_features:
            df = petro.calculate_FI(df)

        if "LI" in petrophysical_features:
            df = petro.calculate_LI(df)

        if "AI" in petrophysical_features:
            df = petro.calculate_AI(df)

        if "CALI-BS" in petrophysical_features:
            df = petro.calculate_CALI_BS(df)

        if "VSH" in petrophysical_features:
            df = petro.calculate_VSH(df, **kwargs)

    return df


def add_well_metadata(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Adds well metadata columns to the provided dataframe from the provided
    well metadata dictionary (kwarg)

    Warning:
        This method will not work without the three kwargs listed below! It will
        return the df untouched and print a warning if kwargs are missing.

    Args:
        df (pd.DataFrame): The dataframe in which the well metadata columns will
            be added

    Keyword Args:
        metadata_dict (dict): The dictionary containing the relevant metadata
            per well (usually generated with the
            :py:meth: `get_well_metadata <akerbp.mlpet.utilties.get_well_metadata>` function).
        metadata_columns (list): List of metadata columns to add (each entry must
            correspond to a metadata key in the provided metadata_dict kwarg)
        id_column (str): The name of the column containing the well names (to be
            matched with the keys in the provided metadata_dict)
        retrieve_from_cdf (bool): Whether to retrieve the metadata from CDF.
            Defaults to true if metadata_dict is not provided.

    Warning:
        If the retrieve_from_cdf kwarg is set to True, an API key must be
        set in the environment variables to allow creation of the client object.

    Returns:
        pd.DataFrame: Return the passed dataframe with the requested columns added
    """
    id_column: str = kwargs.get("id_column", None)
    metadata_dict: Dict[str, Dict[str, Any]] = kwargs.get("metadata_dict", None)
    metadata_columns: List[str] = kwargs.get("metadata_columns", None)
    retrieve_from_cdf: bool = kwargs.get("retrieve_from_cdf", metadata_dict is None)

    if id_column is None:
        raise ValueError("id_column kwarg must be provided")
    if retrieve_from_cdf:
        client = utilities.get_cognite_client()
        try:
            metadata_dict = utilities.get_well_metadata(
                well_names=df[id_column].unique(), client=client
            )
        except Exception as exc:
            raise Exception(
                "Something failed in the retrieval of the formation tops mapping. "
                "Please check the error message below and try again.\n\n"
                f"{exc}"
            ) from exc
    if not all([x is not None for x in [metadata_dict, metadata_columns]]):
        warnings.warn(
            "Could not add metadata because one of the necessary kwargs was "
            "missing! Returning the dataframe untouched."
        )
        return df

    # Reduce metadata dict to only desired columns
    mapper: Dict[str, Dict[str, Any]] = defaultdict(dict)
    for well, meta in metadata_dict.items():
        for k, v in meta.items():
            if k in metadata_columns:
                mapper[k][well] = v

    # Apply metadata mapping
    for column in metadata_columns:
        df[column] = df[id_column].map(mapper[column])

    return df


def add_formations_and_groups(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    """
    Adds a FORMATION AND GROUP column to the dataframe based on the well formation
    tops metadata and the depth in the column.

    Note:
        This function requires several kwargs to be able to run. If they are not
        provided a warning is raised and instead the df is returned untouched.

    Note:
        If the well is not found in formation_tops_mapping, the code will
        print a warning and continue to the next well.

    Example:
        An example mapper dictionary that would classify all depths in WELL_A
        between 120 & 879 as NORDLAND GP and all depths between 879 and 2014 as
        HORDALAND GP, would look like this::

            formation_tops_mapper = {
                "WELL_A": {
                    "labels": [NORDLAND GP, HORDALAND GP],
                    "levels": [120.0, 879.0, 2014.0]
                }
                ...
            }

        It can be generated by using the
        :py:meth: `get_formation_tops <akerbp.mlpet.utilties.get_formation_tops>` function

    Args:
        df (pd.DataFrame): The dataframe in which the formation tops label column
            should be added

    Keyword Args:
        id_column (str): The name of the column of well IDs
        depth_column (str): The name of the depth column to use for applying the
            mappings.
        formation_tops_mapper (dict): A dictionary mapping the well IDs to the
            formation tops labels, chronostrat and depth levels. For example::

                formation_tops_mapper = {
                    "31/6-6": {
                        "group_labels": ['Nordland Group', 'Hordaland Group', ...],
                        "group_labels_chronostrat": ['Cenozoic', 'Paleogene', ...]
                        "group_levels": [336.0, 531.0, 650.0, ...],
                        "formation_labels": ['Balder Formation', 'Sele Formation', ...],
                        "formation_labels_chronostrat": ['Eocene', 'Paleocene', ...],
                        "formation_levels": [650.0, 798.0, 949.0, ...]
                    }
                    ...
                }

            The above example would classify all depths in well 31/6-6 between 336 &
            531 to belong to the Nordland Group, and the corresponding chronostrat is the Cenozoic period.
            Depths between 650 and 798 are classified to belong to the Balder formation,
            which belongs to the Eocene period.
        retrieve_from_cdf (bool): Whether to retrieve the formation tops mapping
            from CDF. False if the mapper is provided directly otherwise it
            defaults to True.

    Warning:
        If the mapper is not provided, the function will attempt to retrieve it
        from CDF. This requires that an API key is set in the environment!

    Returns:
        pd.DataFrame: dataframe with additional columns for FORMATION and GROUP
    """
    id_column: str = kwargs.get("id_column", None)
    depth_column: str = kwargs.get("depth_column", "DEPTH")
    formation_tops_mapper: Dict[
        str, Dict[str, Union[List[str], List[float]]]
    ] = kwargs.get("formation_tops_mapper", {})
    retrieve_from_cdf: bool = kwargs.get("retrieve_from_cdf", not formation_tops_mapper)

    if depth_column not in df.columns:
        raise ValueError(
            "Cannot add formations and groups metadata without a depth_column! "
            "Please provide a depth_column kwarg to the add_formations_and_groups "
            " specifying which column to use as the depth column."
        )

    well_names = df[id_column].unique()
    if retrieve_from_cdf:
        client = utilities.get_cognite_client()
        try:
            formation_tops_mapper = utilities.get_formation_tops(
                well_names=well_names, client=client
            )
        except Exception as exc:
            raise Exception(
                "Something failed in the retrieval of the formation tops mapping. "
                "Please check the error message below and try again.\n\n"
                f"{exc}"
            ) from exc
    df_ = df.copy()
    if id_column is not None and formation_tops_mapper:
        df_["GROUP"] = "UNKNOWN"
        df_["FORMATION"] = "UNKNOWN"

        for well in df_[id_column].unique():
            try:
                mappings = formation_tops_mapper[well]
            except KeyError:
                df_.loc[df_[id_column] == well, ["GROUP", "FORMATION"]] = np.nan
                warnings.warn(
                    f"No formation tops information found for {well}. Setting "
                    "both GROUP and FORMATION to NaN for this well."
                )
                continue

            group_labels, group_levels = (
                mappings["group_labels"],
                mappings["group_levels"],
            )
            formation_labels, formation_levels = (
                mappings["formation_labels"],
                mappings["formation_levels"],
            )

            if (len(group_levels) != len(group_labels) + 1) or (
                len(formation_levels) != len(formation_labels) + 1
            ):
                warnings.warn(
                    f"The formation top information for {well} is invalid! "
                    "Please refer to the docstring of this method to understand "
                    "the format in which formation top mappings should be provided."
                )
                continue

            well_df = df_[df_[id_column] == well]
            df_.loc[well_df.index, "GROUP"] = pd.cut(
                well_df[depth_column],
                bins=group_levels,
                labels=group_labels,
                include_lowest=True,
                right=False,
                ordered=False,
            )

            df_.loc[well_df.index, "FORMATION"] = pd.cut(
                well_df[depth_column],
                bins=formation_levels,
                labels=formation_labels,
                include_lowest=True,
                right=False,
                ordered=False,
            )
        df_["GROUP"] = utilities.map_formation_and_group(
            df_["GROUP"].astype(str).apply(utilities.standardize_group_formation_name)
        )[1]

        df_["FORMATION"] = utilities.map_formation_and_group(
            df_["FORMATION"]
            .astype(str)
            .apply(utilities.standardize_group_formation_name)
        )[0]

    else:
        raise ValueError(
            "A formation tops label could not be added to the provided dataframe"
            " because some keyword arguments were missing!"
        )
    return df_


def add_vertical_depths(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    """Add vertical depths, i.e. TVDKB, TVDSS and TVDBML, to the input dataframe.
    This function relies on a keyword argument for a vertical depth mapper dictionary,
    created by querying CDF at discrete points along the wellbore for each well.
    To map the vertical depths along the entire wellbore, the data in the dictionary is interpolated by using the measured depth

    Args:
        df (pd.DataFrame): pandas dataframe to add vertical depths to

    Keyword Args:
        md_column (str): identifier for the measured depth column in the provided dataframe
            Defaults to None
        id_column (str): identifier for the well column in the provided dataframe
            Defaults to None
        vertical_depths_mapper (dict): dictionary containing vertical- and measured depths
            queried from CDF at discrete points along the wellbore for each well. For example::

                vertical_depths_mapper = {
                    "25/6-2": {
                        "TVDKB": [0.0, 145.0, 149.9998, ...],
                        "TVDSS": [-26.0, 119.0, 123.9998, ...],
                        "TVDBML": [-145.0, 0.0, 4.999799999999993, ...],
                        "MD": [0.0, 145.0, 150.0, ...]
                    }
                }

            Defaults to an empty dictionary, i.e. {}

        retrieve_from_cdf (bool): Whether to retrieve the formation tops mapping
            from CDF. False if the mapper is provided directly otherwise it
            defaults to True.

    Returns:
        pd.DataFrame: dataframe with additional column for TVDKB, TVDSS and TVDBML
    """
    md_column: str = kwargs.get("md_column", None)
    id_column: str = kwargs.get("id_column", None)
    client: CogniteClient = kwargs.get("client", None)
    vertical_depths_mapper: Dict[str, Dict[str, List[float]]] = kwargs.get(
        "vertical_depths_mapper", {}
    )
    retrieve_from_cdf: bool = kwargs.get(
        "retrieve_from_cdf", not vertical_depths_mapper
    )

    if id_column is None:
        raise ValueError("No id_column kwarg provided!")
    if retrieve_from_cdf:
        client = utilities.get_cognite_client()
        try:
            vertical_depths_mapper = utilities.get_vertical_depths(
                well_names=df[id_column].unique(), client=client
            )
        except Exception as exc:
            raise Exception(
                "Something failed in the retrieval of the formation tops mapping. "
                "Please check the error message below and try again.\n\n"
                f"{exc}"
            ) from exc
    if (
        md_column is not None
        and id_column is not None
        and len(vertical_depths_mapper) != 0
    ):
        df_ = df.copy()
        for well in vertical_depths_mapper:
            md_interpolate = df_.loc[df_[id_column] == well, md_column].to_list()
            depths = vertical_depths_mapper[well]
            md = depths["MD"]
            for key in depths.keys():
                if key == "MD":
                    continue
                vertical_depth = depths[key]
                with warnings.catch_warnings(record=True) as w:
                    f = interp1d(x=md, y=vertical_depth, fill_value="extrapolate")
                    interpolated_vertical_depth = f(md_interpolate)
                if w:
                    warnings.warn(
                        f"Interpolating {key} for well {well} triggered a "
                        f"runtime warning: {w[0].message}"
                    )
                df_.loc[df_[id_column] == well, key] = interpolated_vertical_depth
    else:
        raise ValueError(
            "The vertical depths could not be added to the provided dataframe"
            " because some keyword arugments were missing!"
        )
    return df_


def add_depth_trend(df: pd.DataFrame, **kwargs):
    """
    Adds depth trend columns to the dataframe

    Args:
        df (pd.DataFrame): pandas df to add depth trend to

    Keyword Args:
        id_column (str): REQUIRED identifier for the well column in the provided dataframe
            Defaults to None
        client (CogniteClient): OPTIONAL client for querying depth trend function from CDF
            Defaults to None
        env (str): OPTIONAL environment where function is hosted (typically test or prod). Defaults to prod
        version (str): OPTIONAL version of function to be called. Defaults to latest.
        return_CI (bool): OPTIONAL whether to return confidence interval to the trends.
        return_file (bool): OPTIONAL whether to return the predictions as a CDF file link.
            Defaults to True.
        keyword_arguments (dict): OPTIONAL dictionary containing any keywargs for the function call. Eg.
                keyword_arguments = {
                    "nan_textual_value": "-9999.0",
                    "nan_numerical_value": -9999
                }
            Defaults to a dictionary as example above.

    Returns:
        pd.DataFrame: dataframe with added depth trend and optionally its confidence intervals
    """

    id_column: str = kwargs.get("id_column", None)
    client: CogniteClient = kwargs.get("client", None)
    env: str = kwargs.get("env", "prod")
    version: str = kwargs.get("version", None)
    return_CI: bool = kwargs.get("return_CI", False)
    user_kwargs: Dict[str, Any] = kwargs.get("keyword_arguments", None)

    # Keyword arguments dict has to be initialized if None is given by the user
    # as the function cannot accept nan in the input.
    keyword_arguments = {
        "nan_numerical_value": -9999,
        "nan_textual_value": "-9999.0",
    }
    if user_kwargs is not None:
        keyword_arguments.update(user_kwargs)

    # Validate input parameters
    if id_column is None:
        raise ValueError("id column (well name column) is a required kwarg!")
    if version is None:
        version = "latest"
        external_id = f"depth_trend-prediction-{env}"
    else:
        external_id = f"depth_trend-prediction-{env}-{version}"
    df_ = utilities.run_CDF_function(
        df,
        id_column,
        keyword_arguments,
        external_id,
        client,
        return_file=kwargs.get("return_file", True),
    )
    if not return_CI:
        output_curves = [c for c in df_.columns if "_P" not in c]
        return df_[output_curves]
    return df_
