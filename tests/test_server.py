import pytest
from logdatasets._datasets.dataset import MainDataset
import logdatasets.server.dataset_management as dm


DATASET_NAME = "AIT_v2_santos"
SUBSET_NAME = "Intranet-Audit"


def _require_dataset(dataset_name=DATASET_NAME, subset_name=SUBSET_NAME):
    available = dm.get_available_datasets()
    if dataset_name not in available:
        pytest.skip(f"Dataset '{dataset_name}' is not available in this environment.")

    dataset_subsets = available.get(dataset_name, {})
    if subset_name not in dataset_subsets:
        pytest.skip(
            f"Subset '{subset_name}' for dataset '{dataset_name}' is not available in this environment."
        )


class TestCaseChunkData:
    def test_number_chunks(self):
        _require_dataset()
        n_chunks = dm.ChunkMethods.total_num(DATASET_NAME, SUBSET_NAME)
        assert n_chunks >= 1

    def test_get_chunk(self):
        _require_dataset()
        for i in range(dm.ChunkMethods.total_num(DATASET_NAME, SUBSET_NAME)):
            chunk = dm.ChunkMethods.get_chunck(DATASET_NAME, SUBSET_NAME, i + 1)
            assert isinstance(chunk, bytes)

    def test_concatenate_chunk(self):
        _require_dataset()
        n_chunks = dm.ChunkMethods.total_num(DATASET_NAME, SUBSET_NAME)
        chunks = []
        for i in range(n_chunks):
            chunks.append(
                dm.ChunkMethods.get_chunck(DATASET_NAME, SUBSET_NAME, i + 1)
            )

        df = dm.ChunkMethods.concatenate_chunck(chunks).get_data()

        assert MainDataset(
            DATASET_NAME, sub_name=SUBSET_NAME, use_cache=True
        ).get_data().equals(df)


def test_get_available_datasets():
    assert isinstance(dm.get_available_datasets(), dict)
