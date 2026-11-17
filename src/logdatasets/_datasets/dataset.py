from logdatasets._datasets._dataset_op.postprocess import PostProcess
from logdatasets._datasets._dataset_op.labels import LabelSelection
from logdatasets._datasets._dataset_op.cache import Cache
from logdatasets._datasets._dataset_op.stats import Stats

from logdatasets._datasets.list_datasets import overall_datasets
from logdatasets._metrics import do_metrics
import logdatasets._op as op

from detectmateperformance.match_tree import TreeMatcher, LogTemplates
from detectmateperformance.autoparser import AutoParse

from tabulate import tabulate
import polars as pl
import numpy as np


class Dataset:
    def __init__(self, name: str, df: pl.DataFrame | pl.LazyFrame) -> None:
        self.name = name
        self.data = df
        self.size = 0

    def __str__(self) -> str:
        line = "\033[45m" + "".join([" " for _ in range(100)]) + "\033[0m\n"
        return f"\033[45m<Dataset: {self.name}>\033[0m\n{line}{self.get_stats()}\n{line}"
    
    def get_dict(self) -> dict[str, str]:
        if isinstance(data := self.get_data(), pl.DataFrame):
            return Stats.from_df(data, n_memory=self.size)
        return Stats.from_lazy(data, n_memory=self.size)
    
    def __len__(self) -> int:
        if isinstance(self.get_data(), pl.LazyFrame):
            return self.get_data().select(pl.len()).collect().item()
        return len(self.get_data())

    def get_metrics(
        self, pred: list[bool], do_print: bool = True, window_size: int = 1, skip: int = 0
    ) -> dict:
        """`skip` drops the first `skip` rows from the scoring window, so a detector's
        warm-up rows can be excluded. skip=0 scores everything (streaming behaviour).
        Only Labels goes on: the metric counts filter the frame, and on an eager frame a
        filter copies every column (HDFS: +2 GB per scoring step)."""
        df = self.get_data().select("Labels")
        if skip:
            df, pred = df.slice(skip), pred[skip:]
        return do_metrics(df=df, pred=pred, do_print=do_print, window_size=window_size)

    def get_stats(self) -> str:
        return tabulate(self.get_dict(), tablefmt="double_outline")
    
    def get_data(self) -> pl.DataFrame | pl.LazyFrame:
        return self.data
    
    def get_not_found(self) -> list[str]:
        data = self.data.filter(pl.col("Templates") == "template not found")
        return data["Content"].unique().to_list() 

    def remove_anomalies(self, from_: int, to_: int) -> int:
        n = self.get_data().slice(from_, to_ - from_).filter(pl.col("Labels") == 1)
        n = len(n) if isinstance(n, pl.DataFrame) else n.select(pl.len()).collect().item()

        row_indices = pl.int_range(0, pl.len())
        self.data = self.data.remove(
             ((row_indices >= from_) & (row_indices < to_) & (pl.col("Labels") == 1))
        )
        return n


def process_dataset(dataset: dict[str, str], path: str, name: str) -> None:
    log_file = path + dataset["Paths"]
    if dataset["Multiple logs"]:
        log_file = op.get_paths(log_file, dataset["Pattern"])

    if "regex" in dataset:
        regex = dataset["regex"]
        tree_matcher= TreeMatcher(LogTemplates(dataset["templates"]))
        
    else: 
        tree_matcher, regex = AutoParse()(log_file, log_type=dataset["LogType"])
    df = tree_matcher(
        log_file, get_var=True, regex=regex, n_workers=10, batch=int(3e+6)
    )
  
    # TODO: until there is a better metod to dial with DNSmasq exception, this stay here
    if "DNSmasq" in name and len(df.filter(pl.col("Templates") == "template not found")) == len(df):
        regex = r'(?P<Month>\S+)  (?P<Day>\S+) (?P<Time>\S+) (?P<Value>\S+) (?P<Content>.*)'
        df = tree_matcher(
            log_file, get_var=True, regex=regex, n_workers=10, batch=int(3e+6)
        )
    if dataset.get("LogType", "") in dir(PostProcess):
        df: pl.DataFrame = getattr(PostProcess, dataset["LogType"])(df)
    if dataset.get("Labels_type", "") in dir(LabelSelection) and dataset["Labels"] is not None:
        df: pl.DataFrame = getattr(LabelSelection, dataset["Labels_type"])(df, path + dataset["Labels"])

    print("⚙️  Processing and sorting by time...")
    time = df.with_columns(pl.col("Timestamp").cast(float))["Timestamp"].to_numpy()
    idx =  np.argsort(time, descending=False)
    df = df[idx]           

    Cache.save(name, df)
    print("✅ Data saved in cache!", name)


class MainDataset(Dataset):
    def __init__(
        self, name: str, use_cache: bool = True, sub_name: str = "", do_download: bool = True
    ) -> None:
        
        name_ = name + "_" + sub_name if sub_name != "" else name
        if use_cache and (data := Cache.check_and_load(name_)) is not None:
            print("✅ Dataset was already downloaded before!")
        elif do_download:
            if "PrePath" in overall_datasets[name]:
                print("🗃️ Loading presaved dataset")
                self._process(name)
            else:
                print("⬇️  Dataset not found, starting download...")
                self._download(name)
            data = Cache.check_and_load(name_)
        else:
            print("ℹ️  Dataset not downloaded")
            data = pl.DataFrame()

        super().__init__(name_, df=data)
        self.size = Cache.get_size(name_)

    @classmethod
    def from_Dataset(
        cls, name: str, sub_name: str, dataset: Dataset, save_cache: bool = False
    ) -> "MainDataset":
        cls_dataset = cls(name=name, use_cache=False, sub_name=sub_name, do_download=False)
        cls_dataset.data = dataset.get_data()

        if save_cache:
            Cache.save(cls_dataset.name, cls_dataset.get_data())
            print("✅ Data saved in cache!", name)

        return cls_dataset

    def _download(self, name: str) -> None:
        op.create_temp()
        path = op.download_file(overall_datasets[name]["URL"])
        path = op.unzip(path)
        path = ".temp/unzip_folder"

        if "List" not in overall_datasets[name]:
            process_dataset(dataset=overall_datasets[name], path=path, name=name)
        else:
            for dataset in overall_datasets[name]["List"]:
                process_dataset(dataset=dataset, path=path, name=name + "_" + dataset["Name"])

        op.remove_temp()

    def _process(self, name: str) -> None:
        path = op.unzip(overall_datasets[name]["PrePath"])
        path = path + overall_datasets[name]["Paths"]

        Cache.save(name, pl.read_parquet(path))
        print("✅ Data saved in cache!", name)
