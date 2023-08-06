import os

from cognite.client import CogniteClient

from akerbp.mlpet.dataloader import DataLoader

api_key = os.getenv("COGNITE_API_KEY_PERSONAL")
if api_key is not None:
    client = CogniteClient(
        client_name="test", project="akbp-subsurface", api_key=api_key
    )
else:
    # Assuming COGNITE_API_KEY is set in the environment
    client = CogniteClient(client_name="test", project="akbp-subsurface")


def test_load_from_cdf():
    dl = DataLoader()
    df = dl.load_from_cdf(
        client=client, metadata={"wellbore_name": "25/2-7", "subtype": "BEST"}
    )
    assert df.shape[0] > 0


def test_load_from_las():
    dl = DataLoader()

    dl.load_from_las(
        [
            "src/akerbp/mlpet/tests/data/15_9-23.las",
            "src/akerbp/mlpet/tests/data/25_2-7.las",
            "src/akerbp/mlpet/tests/data/35_12-1.las",
        ]
    )
