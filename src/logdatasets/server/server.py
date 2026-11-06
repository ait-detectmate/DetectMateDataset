import logdatasets.server.dataset_management as dm

from fastapi import FastAPI, status, HTTPException
import uvicorn
import base64


def int_convert(value: str) -> int:
    try:
        return int(value)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


app = FastAPI()

datasets = dm.get_available_datasets()


@app.get("/get_num_chunks", status_code=status.HTTP_200_OK)
def get_num_chunks(dataset: str, subdataset: str = "") -> dict:
    if dm.is_dataset_available(datasets, dataset, subdataset):
        return {
            "name": dataset,
            "subdataset": subdataset,
            "size": 0,
            "is_available": False,
        }

    size = dm.ChunkMethods.total_num(dataset, subdataset)
    return {
        "name": dataset,
        "subdataset": subdataset,
        "size": size,
        "is_available": True,
    }


@app.get("/get_chunk", status_code=status.HTTP_200_OK)
def get_chunk(dataset: str, chunk: str, subdataset: str = "") -> dict:
    if dm.is_dataset_available(datasets, dataset, subdataset):
        return {
            "name": dataset,
            "subdataset": subdataset,
            "is_available": False,
            "chunk": bytes(""),
        }

    chunk = int_convert(chunk)
    was_succesful, chunk_value = dm.get_chunk(datasets, dataset, subdataset, chunk=chunk)
    if not was_succesful:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not succesful to get chunk",
        )
    
    return {
            "name": dataset,
            "subdataset": subdataset,
            "is_available": True,
            "chunk": base64.b64encode(chunk_value).decode("ascii"),
        }


def start_server():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )