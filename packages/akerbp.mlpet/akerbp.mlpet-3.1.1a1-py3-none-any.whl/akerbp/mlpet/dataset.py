import os
import warnings
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import numpy as np
import pandas as pd
import yaml
from pandas.core.frame import DataFrame
from tqdm.auto import tqdm

import akerbp.mlpet.data.mappings as default_mappings
import akerbp.mlpet.dataloader as dl
import akerbp.mlpet.feature_engineering as feature_engineering
import akerbp.mlpet.imputers as imputers
import akerbp.mlpet.preprocessors as preprocessors
import akerbp.mlpet.utilities as utilities


class Dataset(dl.DataLoader):
    """
    The main class representing a dataset

    Note:
        **All settings on the first level of the settings dictionary/YAML passed
        to the class instance are set as class attributes**

    Warning:
        **ALL** filepaths (regardless of whether it is directlty passed to the
        class at instantiation or in the settings.yaml file) **MUST** be specified
        in absolute form!

    Note: The id_column is always considered a categorical variable!

    Args:
        settings: dict or path to a yaml file. If a path is provided it must
            be provided as an absolute path. The possible keys for the settings:

                - id_column (required): name of the id column, eg. well_name
                - depth_column (optional): name of the measured depth column, e.g. "DEPTH"
                - label_column (optional): name of the column containing the labels
                - num_filler (optional - default 0): filler value for numerical curves(existing or wishing value for replacing missing values)
                - cat_filler (optional - default 'MISSING'): filler value categorical curves(existing or wishing value for replacing missing values)
                - categorical_curves (optional - default [id_column]): The curves to be considered as categorical when identifying which column as numerical
                    (this setting is used several places throughout the library and can be nice to have defined in advance)
                - keep_columns (optional - default []): If you would like to keep some of the columns passed in your dataframe that will not be part
                    of the preprocessing_pipeline you define but should still make part of the preprocessed dataframe, this setting enables that.
                - preprocessing_pipeline (optional - default None): The list of preprocessing functions to be run when the classes' preprocess function is called.
                    If this is not provided, the pipeline **MUST** be provided in the preprocess call. Each key in the preprocessing_pipeline can have the relevant
                    kwargs for that particular preprocessor as it's value. All passed kwargs are parsed and saved to the class instance where relevant for use as
                    defaults in the preprocessing functions

        folder_path: The path to where preprocessing artifacts are stored/shall
            be saved to. Similar to the other two arguments this path must be
            provided as an absolute path.
        mappings: (optional) dict or path to a yaml file. If a path is provided it must
            be provided as an absolute path. Any provided mappings will override
            the internal mappings in MLPet on a key-by-key basis

    """

    # Setting type annotations for class attributes that can be set when an
    # instance of the Dataset class is created
    settings: Dict[str, Any]
    settings_path: str
    all_curves: Set[str]
    id_column: str
    label_column: str
    num_filler: float
    cat_filler: str
    mappings: Dict[str, Any]
    categorical_curves: List[str]
    petrophysical_features: List[str]
    keep_columns: List[str]
    preprocessing_pipeline: Dict[str, Dict[str, Any]]

    def __set_defaults(self) -> None:
        """
        Set necessary defaults for proper class use
        """
        if not hasattr(self, "num_filler"):
            self.num_filler = 0

        if not hasattr(self, "cat_filler"):
            self.cat_filler = "MISSING"

        if not hasattr(self, "keep_columns"):
            self.keep_columns = []

    def __handle_paths(self, path: Union[Path, str]) -> Union[Path, str]:
        """
        A helper function to handle paths passed either directly to the class
        or via the settings file

        Args:
            path (Union[Path, str]): A filepath to be handled

        Raises:
            ValueError: Raises a ValueError is the path provided is not absolute-

        Returns:
            Union[Path, str]: Returns the path handled.
        """
        if not os.path.isabs(path):
            raise ValueError(
                "All paths must be passed as absolute paths. This is done for "
                "consistency! (HINT: You can import os and simply wrap a "
                "os.path.abspath() call around your path.)"
            )
        return path

    def __ingest_pipeline(
        self, preprocessing_pipeline: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        A helper function to ingest preprocessing pipelines

        Args:
            preprocessing_pipeline (Dict[str, Dict[str, Any]]): The
                preprocessing pipeline to ingest
        """
        for func_name, kwargs in preprocessing_pipeline.items():
            try:
                for setting_name, setting in kwargs.items():
                    local = getattr(self, setting_name, None)
                    if local is not None:
                        warnings.warn(
                            "This class instance already has a value set for "
                            f"{setting_name}. You are overwriting "
                            f"it's value {local} with {setting}!"
                        )
                    setattr(self, setting_name, setting)
            except Exception as e:
                raise Exception(
                    f"Something is wrong in your specification for the {func_name} "
                    "function in your preprocessing_pipeling!"
                ) from e

    def __standardize_curves(self) -> None:
        """
        A helper function to standardize curve names.

        """
        # First need to compile a single list of all curves across all methods
        # MAKE SURE TO KEEP THIS LIST UPDATED!
        curve_sets = [
            "curves_to_scale",
            "curves_to_normalize",
            "curves_to_select",
            "curves_to_drop",
            "curves_to_impute",
            "columns_to_encode",
            "rolling_features",
            "gradient_features",
            "log_features",
            "sequential_features",
            "petrophysical_features",
            "noisy_curves",
            "outlier_curves",
            "numerical_curves",
            "categorical_curves",
            "keep_columns",
        ]
        all_curves = {}
        for curve_set in curve_sets:
            if hasattr(self, curve_set):
                all_curves[curve_set] = getattr(self, curve_set)

        # Standardize passed curves if mappings exist
        if hasattr(self, "curve_mappings"):
            for curve_set, curves in all_curves.items():
                setattr(self, f"{curve_set}_original", curves)
                new_names, _ = utilities.standardize_names(
                    names=curves, mapper=self.curve_mappings
                )
                setattr(self, curve_set, new_names)
                all_curves[curve_set] = new_names

        # Clean up all curves to be on one level and unique
        self.all_curves = set(np.concatenate(list(all_curves.values())))

        # Standardize single curves if mappings exist
        curves = {"id_column": self.id_column}
        if hasattr(self, "label_column"):
            curves["label_column"] = self.label_column
        if hasattr(self, "depth_column"):
            curves["depth_column"] = self.depth_column
        if hasattr(self, "curve_mappings"):
            for curve_label, curve_name in curves.items():
                new_name, _ = utilities.standardize_names(
                    [curve_name], mapper=self.curve_mappings
                )
                setattr(self, curve_label, new_name[0])
                setattr(self, f"{curve_name}_original", curve_name)
                curves[curve_label] = new_name[0]

        # Add all single curves to all_curves
        self.all_curves.update(list(curves.values()))

        # If preprocessing exists, ensure to update it with all the new
        # curve names
        if hasattr(self, "preprocessing_pipeline"):
            for func_name, kwargs in self.preprocessing_pipeline.items():
                for setting_name, _ in kwargs.items():
                    if setting_name not in curve_sets and setting_name not in list(
                        curves
                    ):
                        # Avoid non curve related settings
                        continue
                    # No default for getattr. At this point if the attribute
                    # doesn't exist an error should be raised
                    self.preprocessing_pipeline[func_name][setting_name] = getattr(
                        self, setting_name
                    )

    def __ingest_init_input(
        self, att_name: str, att_val: Union[str, Dict[str, Any], Path]
    ) -> None:
        if isinstance(att_val, dict):
            setattr(self, att_name, att_val)
        elif isinstance(att_val, str):
            att_val = self.__handle_paths(att_val)
            if os.path.isfile(att_val):
                att_path = f"{att_name}_path"
                setattr(self, att_path, att_val)
                with open(getattr(self, att_path)) as file:
                    setattr(self, att_name, yaml.load(file, Loader=yaml.SafeLoader))
            else:
                raise FileNotFoundError(
                    f"The provided filepath {att_val} is not a valid path! "
                    f"The Dataset cannot be initialised without a {att_name}.yaml!"
                    " Please refer to the classes' docstring to ensure you have"
                    " specified your filepath in the correct form."
                )

    def __init__(
        self,
        settings: Union[str, Dict[str, Any]],
        folder_path: Union[str, Path],
        mappings: Optional[Union[str, Dict[str, str]]] = None,
    ) -> None:
        # Define supported preprocessing functions
        self.supported_preprocessing_functions = {
            f.__name__: f
            for f in [
                feature_engineering.add_log_features,
                feature_engineering.add_gradient_features,
                feature_engineering.add_rolling_features,
                feature_engineering.add_sequential_features,
                feature_engineering.add_formations_and_groups,
                feature_engineering.add_vertical_depths,
                feature_engineering.add_petrophysical_features,
                imputers.impute_depth_trend,
                preprocessors.set_as_nan,
                preprocessors.remove_outliers,
                preprocessors.remove_small_negative_values,
                preprocessors.fill_zloc_from_depth,
                preprocessors.fillna_with_fillers,
                preprocessors.encode_columns,
                preprocessors.select_columns,
                preprocessors.normalize_curves,
                preprocessors.scale_curves,
                preprocessors.process_wells,
                preprocessors.remove_noise,
                preprocessors.drop_columns,
            ]
        }
        # <--------------------- INGEST INIT INPUTS -------------------------> #

        self.__ingest_init_input(att_name="settings", att_val=settings)
        for key, val in self.settings.items():
            setattr(self, key, val)

        if mappings is None:
            self.mappings = default_mappings.base_mappings
        else:
            self.__ingest_init_input(att_name="mappings", att_val=mappings)
            # Any keys in the provided mappings override the base mappings
            try:
                curve_mappings = default_mappings.base_mappings["curve_mappings"]
                curve_mappings.update(self.mappings["curve_mappings"])
                self.mappings["curve_mappings"] = curve_mappings
            except KeyError:
                self.mappings["curve_mappings"] = default_mappings.base_mappings[
                    "curve_mappings"
                ]
                pass
            try:
                formations_map = default_mappings.base_mappings["formations_map"]
                formations_map.update(self.mappings["formations_map"])
                self.mappings["formations_map"] = formations_map
            except KeyError:
                self.mappings["formations_map"] = default_mappings.base_mappings[
                    "formations_map"
                ]
                pass
            try:
                groups_map = default_mappings.base_mappings["groups_map"]
                groups_map.update(self.mappings["groups_map"])
                self.mappings["groups_map"] = groups_map
            except KeyError:
                self.mappings["groups_map"] = default_mappings.base_mappings[
                    "groups_map"
                ]
                pass
        self.curve_mappings = self.mappings["curve_mappings"]
        self.formations_map = self.mappings["formations_map"]
        self.groups_map = self.mappings["groups_map"]

        # Ensure required settings were provided to prevent problems later down the line
        required = ["id_column"]
        for r in required:
            if not hasattr(self, r):
                raise AttributeError(
                    f"{r} was not set in your settings file! This setting is "
                    "required. Please refer to the docstring."
                )

        self.folder_path = self.__handle_paths(folder_path)
        if not os.path.isdir(self.folder_path):
            os.makedirs(self.folder_path)

        # Ingest the preprocessing kwargs if a preprocessing_pipeline was passed
        if hasattr(self, "preprocessing_pipeline"):
            self.__ingest_pipeline(self.preprocessing_pipeline)
            # Ensure all functions are supported
            for func_name in self.preprocessing_pipeline:
                if func_name not in self.supported_preprocessing_functions:
                    raise ValueError(
                        f"The function {func_name} is not a supported "
                        "preprocessing function. All function specifications "
                        "passed in the preprocessing_pipeline must be a subset "
                        "of the supported preprocessing functions: "
                        f"{list(self.supported_preprocessing_functions)}"
                    )

        # Fill missing gaps for parameters that are required for proper operation
        # of this class
        self.__set_defaults()

        # <------------------ PERFORM INPUT CHECKS---------------------------> #

        # Standardize curve names and create all_curves attribute, update settings with new curve names
        self.__standardize_curves()

        # Check that categorical curves includes the id_column (to prevent
        # unnesscary warnings later on)
        if hasattr(self, "categorical_curves"):
            self.categorical_curves = list(
                set(self.categorical_curves + [self.id_column])
            )
        else:
            self.categorical_curves = [self.id_column]

    def preprocess(self, df: DataFrame = None, verbose=True, **kwargs) -> DataFrame:
        """
        Main preprocessing function. Pass the dataframe to be preprocessed along
        with any kwargs for running any desired order (within reason) of the
        various supported preprocessing functions.

        To see which functions are supported for preprocessing you can access
        the class attribute 'supported_preprocessing_functions'.

        To see what all the default settings are for all the supported preprocessing
        functions are, run the class 'get_preprocess_defaults' method without any
        arguments.

        To see what kwargs are being used for the default workflow, run the
        class 'get_preprocess_defaults' with the class attribute
        'default_preprocessing_workflow' as the main arg.

        Warning:
            The preprocess function will run through the provided kwargs in the
            order provided by the kwargs dictionary. In python 3.7+, dictionaries
            are insertion ordered and it is this implemnetational detail this function
            builds upon. As such, do not use any Python version below 3.7 or ensure
            to pass an OrderedDict instance as your kwargs to have complete control
            over what order the preprocessing functions are run in!

        Args:
            df (pd.Dataframe, optional): dataframe to which apply preprocessing.
                If none is provided, it will use the class' original df if exists.
            verbose (bool, optional): Whether to display some logs on the progression
                off the preprocessing pipeline being run. Defaults to True.

        Keyword Args:
            See above in the docstring on all potential kwargs and their relevant
            structures.

        Returns:
            pd.Dataframe: preprocessed dataframe
        """
        # <---------------- Perform admin/prep work -------------------------> #
        # If no dataframe is provided, use class df_original
        if df is None:
            if hasattr(self, "df_original"):
                df = self.df_original.copy()
                if df.empty:
                    raise ValueError(
                        "The class connected pd.Dataframe ('df_original') has "
                        "no data so there is nothing to preprocess!"
                    )
            else:
                raise ValueError(
                    "This Dataset class instance does not have a pd.DataFrame "
                    "attached to it so there is no data to preprocess!"
                )

        # Ingest the kwargs to the class instance, if the pipeline was defined
        # in the settings file it will have already been ingested when the class
        # was instantiated so no need to do it here
        if kwargs:
            self.__ingest_pipeline(kwargs)

        # Standardize settings curve names and create all_curves attribute
        self.__standardize_curves()

        # Map curve names in the provided dataframe
        df = utilities.standardize_curve_names(df=df, mapper=self.curve_mappings)

        # Keep track of original column names
        original_columns = set(df.columns)

        # Validate data once kwargs have been ingested and standardized,
        # and the columns of the provided df has been standardized
        df = self.__validate_data(df)

        # Retain only the curves required for preprocessing - the all_curves
        # attribute will have been defined by this point either at instantiation
        # or from the call above to standardize_curves
        diff = original_columns - self.all_curves
        if diff:
            warnings.warn(
                "The following columns were passed in the preprocessing "
                "dataframe but are not used in any of the functions defined in "
                "the defined preprocessing pipeline. As such they will be "
                f"dropped! {list(diff)}"
            )
            df = df.drop(columns=diff)

        # Define kwargs to be used in preprocess method calls
        if not kwargs:
            # User did not provide any kwargs so checking they were provided at
            # instantiation via the settings file. Taking a deepcopy because
            # we don't want to mutate the original pipeline with general defaults
            # in case it is to be used again later
            msg = (
                "No preprocessing kwargs were passed (either at runtime or "
                "via the settings file at instantiation). There's nothing "
                "to preprocess!"
            )
            if hasattr(self, "preprocessing_pipeline"):
                if self.preprocessing_pipeline is not None:
                    kwargs = deepcopy(self.preprocessing_pipeline)
                else:
                    raise ValueError(msg)
            else:
                raise ValueError(msg)

        # Fill in the blanks where necessary
        kwargs = self.get_preprocess_defaults(kwargs)

        # <---------------- Perform preprocessing pipeline ------------------> #
        pbar = tqdm(
            kwargs.items(), desc="Preprocessing", disable=(not verbose), unit="function"
        )
        artifacts = {}
        for function, settings in pbar:
            if verbose:
                tqdm.write(f"Running {function}")
            try:
                res = self.supported_preprocessing_functions[function](df, **settings)
            except Exception as e:
                raise Exception(
                    f"Running {function} failed! Please see the traceback to understand what could have caused the issue:"
                ) from e
            if isinstance(res, tuple):
                # There are artifacts to be saved back to the class. Save them
                df, artifact = res
                # Artifacts must be passed back in dict form where the key is
                # the name the artifact should be saved to this class as
                # and the value is the artifact itself
                if isinstance(artifact, dict):
                    # safe to proceed with saving to cls
                    for k, v in artifact.items():
                        setattr(self, k, v)
                    artifacts.update(artifact)
                else:
                    ValueError(
                        "A preprocessing function that doesn't return only a "
                        "pd.DataFrame MUST return a tuple where the first item "
                        "is the manipulated pd.DataFrame and the second item is "
                        "a dict of artifacts to be saved back to the class "
                        "instance. The dictionary's keys should be the "
                        "attribute name under which the artifact shall be saved "
                        "and the values should be the artifacts themselves."
                    )
            elif isinstance(res, pd.DataFrame):
                df = res
            else:
                raise ValueError(
                    f"The preprocessing function {function} returned an illegal return type!"
                )

        # Perform admin work on detecting features created and removed and
        # artifacts created
        self.features_added = list(
            set([x for x in df.columns if x not in original_columns])
        )
        self.original_columns_removed = list(
            set([x for x in original_columns if x not in df.columns])
        )
        if artifacts:
            self.artifacts = artifacts

        return df

    def get_preprocess_defaults(
        self, kwargs: Dict[str, Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Wrapper function to define and provide the default kwargs to use for
        preprocessing. This function allows the user to only tweak certain
        function kwargs rather than having to define a setting for every single
        function kwargs. If a kwargs dictionary is passed to the function, only
        the defaults for the provided function names found in the kwargs will be
        returned. In other words, to generate a full default kwargs example, run
        this method without any arguments.

        Args:
            kwargs (Dict[str, Any], optional): Any user defined kwargs that should
                override the defaults. Defaults to {}.

        Returns:
            Dict[str, Any]: A populated kwargs dictionary to be passed to all
                supported methods in preprocessing.
        """
        # Define per method defaults
        defaults: Dict[str, Dict[str, Any]] = {
            "add_log_features": {"log_features": getattr(self, "log_features", None)},
            "add_gradient_features": {
                "gradient_features": getattr(self, "gradient_features", None)
            },
            "add_rolling_features": {
                "rolling_features": getattr(self, "rolling_features", None),
                "window": getattr(self, "window", None),
            },
            "add_sequential_features": {
                "sequential_features": getattr(self, "sequential_features", None),
                "shift_size": getattr(self, "shift_size", 5),
            },
            "add_formations_and_groups": {
                "id_column": self.id_column,
                "depth_column": getattr(self, "depth_column", None),
            },
            "add_vertical_depths": {
                "id_column": self.id_column,
                "md_column": getattr(self, "depth_column", None),
            },
            "add_petrophysical_features": {
                "petrophysical_features": getattr(self, "petrophysical_features", None),
                "id_column": self.id_column,
            },
            "simple_impute": {
                "categorical_curves": getattr(self, "categorical_curves", None),
                "depth_column": getattr(self, "depth_column", None),
            },
            "iterative_impute": {
                "imputer": getattr(self, "imputer", None),
            },
            "impute_depth_trend": {
                "curves_to_impute": getattr(self, "curves_to_impute", None),
                "imputation_models": getattr(self, "imputation_models", None),
                "save_imputation_models": getattr(
                    self, "save_imputation_models", False
                ),
                "allow_individual_models": getattr(
                    self, "allow_individual_models", True
                ),
                "folder_path": self.folder_path,
                "curves_mapping": getattr(self, "curve_mappings", None),
            },
            "set_as_nan": {
                "categorical_value": getattr(self, "categorical_value", None),
                "categorical_curves": getattr(self, "categorical_curves", None),
                "numerical_value": getattr(self, "numerical_value", None),
                "numerical_curves": getattr(self, "numerical_curves", None),
            },
            "remove_outliers": {
                "outlier_curves": getattr(self, "outlier_curves", None),
                "threshold": getattr(self, "threshold", 0.05),
            },
            "remove_small_negative_values": {
                "numerical_curves": getattr(self, "numerical_curves", None),
                "nan_threshold": getattr(self, "nan_threshold", None),
            },
            "fill_zloc_from_depth": {},
            "fillna_with_fillers": {
                "num_filler": getattr(self, "num_filler", 0),
                "numerical_curves": getattr(self, "numerical_curves", None),
                "cat_filler": getattr(self, "cat_filler", "MISSING"),
                "categorical_curves": getattr(self, "categorical_curves", None),
            },
            "encode_columns": {
                "columns_to_encode": getattr(
                    self, "columns_to_encode", getattr(self, "categorical_curves", None)
                ),
                "formations_map": getattr(self, "formations_map", None),
                "groups_map": getattr(self, "groups_map", None),
                "missing_encoding_value": getattr(self, "missing_encoding_value", -1),
            },
            "select_columns": {
                "curves_to_select": getattr(self, "curves_to_select", None),
                "label_column": self.label_column,
                "id_column": self.id_column,
            },
            "drop_columns": {
                "curves_to_drop": getattr(self, "curves_to_drop", None),
            },
            "normalize_curves": {
                "low_perc": getattr(self, "low_perc", 0.05),
                "high_perc": getattr(self, "high_perc", 0.95),
                "save_key_wells": getattr(self, "save_key_wells", False),
                "curves_to_normalize": getattr(self, "curves_to_normalize", None),
                "id_column": self.id_column,
                "user_key_wells": getattr(self, "user_key_wells", None),
                "folder_path": self.folder_path,
            },
            "scale_curves": {
                "scaler_method": getattr(self, "scaler_method", "RobustScaler"),
                "scaler": getattr(self, "scaler", None),
                "save_scaler": getattr(self, "save_scaler", False),
                "folder_path": self.folder_path,
                "curves_to_scale": getattr(self, "curves_to_scale", None),
                "scaler_kwargs": getattr(self, "scaler_kwargs", {}),
            },
            "process_wells": {
                "id_column": self.id_column,
                "imputation_type": getattr(self, "imputer", None),
            },
            "remove_noise": {
                # Default behaviour is to apply to all numeric cols
                "noisy_curves": getattr(self, "noisy_curves", None),
                "noise_removal_window": getattr(self, "noise_removal_window", None),
            },
        }

        # Process wells uses a bunch of lower level functions so we need to
        # enrich it's kwargs with the relevant kwargs
        methods_used_by_process_wells = [
            "simple_impute",
            "iterative_impute",
            "add_rolling_features",
            "add_gradient_features",
            "add_sequential_features",
        ]
        for method in methods_used_by_process_wells:
            defaults["process_wells"].update(defaults[method])

        # Ingest defaults into kwargs if they exist
        if kwargs is not None:
            for function_name in kwargs:
                # retrieve default settings for function
                default_function_settings = defaults[function_name]
                # Populate kwargs with all non provided defaults
                for setting_name, default_setting in default_function_settings.items():
                    set_result = kwargs[function_name].setdefault(
                        setting_name, default_setting
                    )
                    # Need to perform some more advanced operations for specifically mapping
                    # dictionaries
                    # First, if the setting is of type dict (e.g. a mapping dict)
                    # need to ensure that we preserve the users mapping and combine
                    # them with any existing mappings created for example upon
                    # class initialisation.
                    if isinstance(set_result, dict) and set_result != default_setting:
                        if setting_name in [
                            "formations_map",
                            "groups_map",
                            "curves_mapping",
                        ]:  # Append/Overwrite user provided mappings to existing mappings
                            kwargs[function_name][setting_name] = {
                                **default_setting,
                                **set_result,
                            }

            return kwargs

        return defaults

    def __validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Checks that the data loaded into the Dataset includes the expected curves
        and returns the validated dataframe

        Note:
            This is an internal class method inly supposed to use once the
            all_curves attribute of the class has been created.

        Args:
            df (pd.DataFrame): The dataframe to be validated

        Returns:
            pd.DataFrame: Returns the validated Dataframe
        """
        # check that all expected curves are present in the data
        expected_but_missing_curves = self.all_curves - set(df.columns.tolist())

        # Remove curves to be generated (petrophysical features)
        if hasattr(self, "petrophysical_features"):
            expected_but_missing_curves -= set(self.petrophysical_features)

        # Remove label column if this a prediction call and the label column is
        # therefore intentionally not in the dataframe:
        if hasattr(self, "label_column"):
            expected_but_missing_curves -= set([self.label_column])

        # Special case for depth column, if its iniitialised by doesn't exist in the dataframe
        # we don't want to fill it with num_filler. Instead we should raise an error
        if hasattr(self, "depth_column"):
            if self.depth_column not in df.columns:
                raise ValueError(
                    f"Depth column {self.depth_column} was set in your settings"
                    " file/preprocessing kwargs but could not be found in the "
                    "provided dataframe. Cannot continue without a proper depth "
                    "column."
                )

        if expected_but_missing_curves:
            expected_but_missing_cat_curves = expected_but_missing_curves & set(
                self.categorical_curves
            )
            expected_but_missing_num_curves = (
                expected_but_missing_curves - expected_but_missing_cat_curves
            )
            warning_msg = (
                "There are curves that are expected but missing from"
                " the provided dataframe. "
            )

            if expected_but_missing_cat_curves:
                warning_msg += (
                    "These curves are being filled with cat_filler: "
                    f"{expected_but_missing_cat_curves}"
                )
            if expected_but_missing_num_curves:
                warning_msg += (
                    "These curves are being filled with num_filler: "
                    f"{expected_but_missing_num_curves}"
                )
            warnings.warn(warning_msg)
            df[list(expected_but_missing_cat_curves)] = self.cat_filler
            df[list(expected_but_missing_num_curves)] = self.num_filler

        return df
