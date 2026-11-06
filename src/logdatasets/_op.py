
from datetime import datetime
from tqdm import tqdm

from pathlib import Path

import requests
import zipfile
import tarfile
import shutil
import json
import os

import polars as pl

temp_folder = ".temp"


def create_temp() -> None:
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)


def remove_temp() -> None:
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)


def unzip(zip_file: str) -> str:

    print("\033[44m >>>> Unziping data      \033[0m")
    print("\033[44m" + "".join([" " for _ in range(100)]) + "\033[0m")
    path = f"{temp_folder}/unzip_folder"

    # download_file always saves as "data.zip" regardless of real format, so
    # detect by content, not extension. tarfile check first: a .tar.gz is not a zip.
    if tarfile.is_tarfile(zip_file):
        with tarfile.open(zip_file, 'r:*') as tar_ref:
            members = tar_ref.getmembers()
            for member in tqdm(
                members, desc="\033[44m  \033[0mExtracting files ⏳",
                unit="file",
                bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
            ):
                tar_ref.extract(member, path, filter='data')
        print(f"\033[44m  \033[0m✅ All {len(members)} files extracted to {path}!")
        print("\033[44m" + "".join([" " for _ in range(100)]) + "\033[0m \n")
        return path

    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            if zip_ref.testzip() is not None:
                raise Exception("File corrupt")

            file_list = zip_ref.namelist()
            total_files = len(file_list)

            for file in tqdm(
                file_list, desc="\033[44m  \033[0mExtracting files ⏳", 
                unit="file", 
                bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
            ):
                zip_ref.extract(file, path)
        print(f"\033[44m  \033[0m✅ All {total_files} files extracted to {path}!")

    except zipfile.BadZipFile:
        print(f"\033[44m  \033[0m ⚠️  Can't uncompress the file, try manually")
        print(f"\033[44m  \033[0m ⚠️  please, save it as unzip_folder")
        print(f"\033[44m  \033[0m ⚠️  folder -> .temp")
        while (msg := input("\033[44m  \033[0m Y: when done, N: to abort: ")) != "Y":
            if msg == "N":
                raise Exception("❌ Abort process")

    print("\033[44m" + "".join([" " for _ in range(100)]) + "\033[0m \n")

    return path


def split_file(path: str) -> list[str]:
    print("\033[44m >>>> Spliting long file      \033[0m")
    print("\033[44m" + "".join([" " for _ in range(100)]) + "\033[0m")

    print("\033[44m  \033[0mCalculating number of lines ⏳")
    with open(path, "rb") as input_file:
        size = sum([1 for _ in input_file])
    print("\033[44m  \033[0m✅ Number of lines:", size)

    files_ = []
    with open(path) as input_file:
        for i in tqdm(
            range(int(size / 10e6)),
            desc="\033[44m  \033[0m Spliting in files ⏳",
            unit="logs",
            bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
        ):
            files_.append(f"{temp_folder}/{i}.log")
            head = []
            for __ in range(int(10e6)):
                try:
                    head.append(next(input_file))
                except UnicodeDecodeError:
                    print(f"\033[44m  \033[0m ⚠️  Unable to read line")
            with open(files_[-1], "w") as f:
                f.writelines(head)

    print("\033[44m" + "".join([" " for _ in range(100)]) + "\033[0m\n")
    return files_
        

def load_file(path_logs) -> list[str]:
    with open(path_logs, "r") as f:
        return f.readlines()


def load_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file) 


def download_file(url: str, chunk_size: int = 4000 ) -> str:

    print("\033[44m >>>> Downloading data      \033[0m")
    print("\033[44m" + "".join([" " for _ in range(100)]) + "\033[0m")

    path = os.path.join(temp_folder, "data.zip")
    flag = False
    for _ in range(10): 
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))

                print("\033[44m  \033[0mURL:", url)
                with open(path, 'wb') as f, tqdm(
                    desc="\033[44m  \033[0m Downloading ⏳",
                    total=total_size,  
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
                ) as bar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        bar.update(len(chunk))
                flag = True
                break
        except requests.exceptions.ChunkedEncodingError:
            print(f"\033[44m  \033[0m ⚠️  Fail, trying again")
            continue

    if not flag:
        raise Exception("❌ Fail to download")
    print(f"\033[44m  \033[0m✅ Download complete!")
    print("\033[44m" + "".join([" " for _ in range(100)]) + "\033[0m \n")

    return path


class AInception:
    @staticmethod
    def is_malicious(label: dict) -> bool:
        return bool(label["malicious"])

    @staticmethod
    def get_timestamp(label: dict) -> str:
        dt = datetime.fromisoformat(label["@timestamp"])
        return dt.timestamp()
    
    @staticmethod
    def assign_labels(df: pl.DataFrame, labels: dict) -> pl.DataFrame:

        print("\033[45m >>>> Assigning data      \033[0m")
        print("\033[45m" + "".join([" " for _ in range(100)]) + "\033[0m")

        df = df.with_row_index()
        df_2 = df.clone().insert_column(-1, pl.col("Time").cast(float).alias("Time_"))

        indices = []
        for label in tqdm(
            labels, 
            desc="\033[45m  \033[0mAssigning labels to logs ⏳",
            bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
        ):
            if AInception.is_malicious(label):
                df_ = df_2.filter(pl.col("Content") == label["message"])
                idx = (df_.with_columns(
                    pl.col("Time_") - AInception.get_timestamp(label)
                )["Time_"]).abs().arg_min()
                indices.extend(df_[idx]["index"].to_list())

        indices = list(set(indices))

        df = df.with_columns(
            pl.when(pl.col("index").is_in(indices)).then(1).otherwise(0).alias("Labels")
        )
        df.drop("index")
        print(f"\033[45m  \033[0m✅ Assign labels complete!")
        print("\033[45m" + "".join([" " for _ in range(100)]) + "\033[0m \n")
        
        return df

    
def get_paths(path_: str, pattern: str) -> str:
    path = Path(path_)
    files = [
        str(f) for f in path.iterdir()
        if f.is_file() and pattern in str(f) and os.path.getsize(str(f)) != 0
    ]
    return [ fil for fil in files ]