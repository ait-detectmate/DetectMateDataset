from logdatasets import api
from logdatasets._datasets.dataset import MainDataset, Dataset

from math import ceil
import polars as pl
import io

CHUNK_SIZE = 500

class ChunkMethods:
    @staticmethod
    def __load_dataset(dataset: str, sub_dataset: str) -> MainDataset:
        return MainDataset(dataset, sub_name=sub_dataset, use_cache=True, do_download=False)

    @staticmethod
    def total_num(dataset: str, sub_dataset: str, chunk_size: int = CHUNK_SIZE) -> int:
        size = len(ChunkMethods.__load_dataset(dataset, sub_dataset))
        return ceil(size / chunk_size)

    @staticmethod
    def get_chunck(
        dataset: str, sub_dataset, chunk: int, chunk_size: int = CHUNK_SIZE
    ) -> bytes:
        return bytes(
            ChunkMethods.__load_dataset(dataset, sub_dataset)
            .get_data()[(chunk - 1) * chunk_size: chunk_size * chunk]
            .serialize()
        )

    @staticmethod
    def concatenate_chunck(chunks: list[bytes]) -> Dataset:
        df = pl.DataFrame.deserialize(chunks[0])
        for chunk in chunks[1:]:
            df = pl.concat([df, pl.DataFrame.deserialize(io.BytesIO(chunk))])

        return Dataset("Obtain", df=df)


def get_available_datasets() -> dict[str, dict[str, int]]:
    datasets = {}
    for dataset in api.get_dataset_names():
        datasets[dataset] = {}
        for subdatset in api.get_sub_dataset_names(dataset):
            if (size := ChunkMethods.total_num(dataset, subdatset)) == 0:
                continue

            datasets[dataset][subdatset] = size

    return datasets


def is_dataset_available(
    datasets: dict[str, dict[str, int]], dataset: str, subdataset: str = ""
):
    return dataset not in datasets or subdataset not in datasets[dataset]


def get_chunk(
    datasets: dict[str, dict[str, int]], dataset: str, sub_datasets: str, chunk: int
) -> tuple[bool, bytes]:
    
    size = datasets[dataset][sub_datasets]
    if 0 >= chunk or chunk > size + 1:
        return False, bytes()

    return True, ChunkMethods.get_chunck(dataset, sub_datasets, chunk=chunk) 