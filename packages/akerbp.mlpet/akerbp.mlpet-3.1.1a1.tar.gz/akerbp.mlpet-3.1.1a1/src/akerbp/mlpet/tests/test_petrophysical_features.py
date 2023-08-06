import numpy as np
import pandas as pd

from akerbp.mlpet import feature_engineering, petrophysical_features
from akerbp.mlpet.dataloader import DataLoader
from akerbp.mlpet.tests.test_feature_engineering import CLIENT as client


def test_guess_bs_from_cali():
    input = pd.DataFrame({"CALI": [6.1, 5.9, 12.0, 12.02]})
    df = petrophysical_features.guess_BS_from_CALI(input)
    assert "BS" in df.columns.tolist()


def test_calculate_cali_bs():
    input = pd.DataFrame({"CALI": np.array([6.1, 5.9, 12.0, 12.02])})
    df = petrophysical_features.calculate_CALI_BS(input)
    assert "CALI-BS" in df.columns.tolist()


def test_calculate_VSH():
    dl = DataLoader()
    df = dl.load_from_cdf(
        client=client, metadata={"wellbore_name": "15/3-5", "subtype": "BEST"}
    )
    df["well_name"] = "15/3-5"
    df = petrophysical_features.calculate_LFI(df)
    df = feature_engineering.add_formations_and_groups(
        df, id_column="well_name", depth_column="DEPTH"
    )
    df = feature_engineering.add_vertical_depths(
        df, id_column="well_name", md_column="DEPTH"
    )
    df_out = petrophysical_features.calculate_VSH(
        df,
        VSH_curves=["GR", "LFI"],
        groups_column_name="GROUP",
        formations_column_name="FORMATION",
        id_column="well_name",
        env="test",
        return_CI=True,
        calculate_denneu=True,
        return_only_vsh_aut=False,
    )
    assert "VSH_AUT" in df_out.columns.tolist()
