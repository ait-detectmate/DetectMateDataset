import logdatasets.server.dataset_management as dm

from logdatasets._datasets.dataset import MainDataset, Dataset

from tqdm import tqdm
import base64
import requests

import polars as pl


def get_number_chunks(
    dataset: str, sub_dataset: str, ip: str = "http://127.0.0.1:8000"
) -> tuple[bool, int]:
    response = requests.get(
        url=f"{ip}/get_num_chunks",
        params={
            "dataset": dataset,
            "subdataset": sub_dataset,
        },
    )

    if response.status_code != 200:
        raise RuntimeError(f"❗❗ Server returned {response.status_code}: {response.text}")
    payload = response.json()

    return payload["is_available"], payload["size"]


def get_chunk(
    dataset: str, sub_dataset: str, chunk: int, ip: str = "http://127.0.0.1:8000"
) -> bytes:
      
    response = requests.get(
        url=f"{ip}/get_chunk",
        params={
            "dataset": dataset,
            "subdataset": sub_dataset,
            "chunk": str(chunk)
        },
    )

    if response.status_code != 200:
        raise RuntimeError(f"❗❗ Server returned {response.status_code}: {response.text}")

    payload = response.json()
    if not payload["is_available"]:
        raise RuntimeError("❗❗ Dataset was not available")

    return base64.b64decode(payload["chunk"])


def get_dataset(
    dataset: str, sub_dataset: str, ip: str = "http://127.0.0.1:8000", save_cache: bool = False
) -> MainDataset:

    print("Geting size of dataset... ⏳")
    is_available, size = get_number_chunks(dataset, sub_dataset=sub_dataset, ip=ip)
    if not is_available:
        print("⚠️ Dataset was not available in server")
        return MainDataset.from_Dataset(
            name=dataset, sub_name=sub_dataset, dataset=Dataset("", pl.DataFrame())
        )

    chunks = []
    for i in tqdm(
        range(1, size + 1), 
        desc="Downloading chunks... ⏳⬇️",
        unit="chunks",
        bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
    ):
        chunks.append(get_chunk(dataset, sub_dataset=sub_dataset, ip=ip, chunk=i))

    downloaded_dataset = dm.ChunkMethods.concatenate_chunck(chunks)
    return MainDataset.from_Dataset(
        name=dataset, sub_name=sub_dataset, dataset=downloaded_dataset, save_cache=save_cache
    )
