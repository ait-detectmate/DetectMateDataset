import os
from pathlib import Path

import polars as pl


cache_path = os.path.join(Path.home(), ".cache/logdata")


def format_bytes(size_bytes: int) -> str:
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


class Cache:
    @staticmethod
    def get_size(file: str) -> str:
        if os.path.exists(path := os.path.join(cache_path, file)):
            size = os.path.getsize(path)
            return format_bytes(size)

        return "0 B"

    @staticmethod
    def check_and_load(file: str) -> pl.DataFrame | None | pl.LazyFrame:
        if not os.path.exists(cache_path):
            Path(cache_path).mkdir(parents=True, exist_ok=True)


        if os.path.exists(path := os.path.join(cache_path, file)):

            if os.path.getsize(path) >= 1e9:
                print("⚠️  File is too heavy, loading it as lazyframe")
                return pl.scan_parquet(path)

            return pl.read_parquet(path)
        return None

    @staticmethod
    def save(file: str, data: pl.DataFrame | pl.LazyFrame) -> None:
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)

        if isinstance(data, pl.LazyFrame):
            data.sink_parquet(os.path.join(cache_path, file))
        else:
            data.write_parquet(os.path.join(cache_path, file))