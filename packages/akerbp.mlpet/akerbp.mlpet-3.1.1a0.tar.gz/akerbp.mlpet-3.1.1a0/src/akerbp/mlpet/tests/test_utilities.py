import os

import yaml
from cognite.client import CogniteClient

from akerbp.mlpet import utilities as utils
from akerbp.mlpet.tests.data.data import (
    FORMATION_TOPS_MAPPER,
    TEST_DF,
    VERTICAL_DEPTHS_MAPPER,
)

api_key = os.getenv("COGNITE_API_KEY_PERSONAL")
if api_key is not None:
    CLIENT = CogniteClient(
        client_name="test", project="akbp-subsurface", api_key=api_key
    )
else:
    # Assuming COGNITE_API_KEY is set in the environment
    CLIENT = CogniteClient(client_name="test", project="akbp-subsurface")
WELL_NAMES = ["25/10-10"]


def test_get_formation_tops():
    formation_tops_mapper = utils.get_formation_tops(WELL_NAMES, CLIENT)
    assert formation_tops_mapper == FORMATION_TOPS_MAPPER


def test_get_vertical_depths():
    retrieved_vertical_depths = utils.get_vertical_depths(WELL_NAMES, CLIENT)
    # empty_queries should be an empty list for the provided WELL_NAMES
    assert retrieved_vertical_depths == VERTICAL_DEPTHS_MAPPER


def test_remove_wo_label():
    df = utils.drop_rows_wo_label(TEST_DF[["AC", "BS"]], label_column="BS")
    assert df.shape[0] == 8


def test_standardize_names():
    mapper = yaml.load(
        open("src/akerbp/mlpet/tests/data/test_mappings.yaml", "r"),
        Loader=yaml.SafeLoader,
    )
    utils.standardize_names(TEST_DF.columns.tolist(), mapper=mapper)


def test_standardize_group_formation_name():
    assert utils.standardize_group_formation_name("ØRN") == "ORN"


def test_get_well_metadata():
    metadata = utils.get_well_metadata(client=CLIENT, well_names=WELL_NAMES)
    assert metadata[WELL_NAMES[0]]["CDF_wellName"] == WELL_NAMES[0]
