import logdatasets._op as op



import polars as pl
from tqdm import tqdm


from datetime import datetime


class LabelSelection:
    @staticmethod
    def AIT_v2(df: pl.DataFrame, labels_path: str) -> pl.DataFrame:
        if labels_path is not None:
            if "apache2" in labels_path:
                paths = op.get_paths(labels_path, "-access.log")
                labels = []
                for path in paths:
                    labels.extend([eval(line)["line"] for line in op.load_file(path)])
                labels = set(labels)
            else:
                labels =  set([eval(line)["line"] for line in op.load_file(labels_path)])

            all_labels = [0 if i not in labels else 1 for i in range(len(df))]
            df = df.insert_column(df.shape[-1], pl.Series("Labels", all_labels))
        return df

    @staticmethod
    def HDFS(df: pl.DataFrame, labels_path: str) -> pl.DataFrame:
        labels = pl.read_csv(labels_path)
        labels = labels.filter(pl.col("Label") == "Anomaly")
        labels = labels.with_columns(pl.col("BlockId").str.replace("blk_", "").cast(int))
        df = df.with_columns(
            pl.col("Content").str.extract(r"\bblk_(-?[0-9]+)").cast(int).alias("block_id")
        )

        df = df.with_columns(
            pl.when(
                pl.col("block_id").is_in(labels["BlockId"].implode())
            ).then(1).otherwise(0).alias("Labels")
        )

        return df.drop("block_id")

    @staticmethod
    def BGL(df: pl.DataFrame, labels_path: str) -> pl.DataFrame:
        df = df.insert_column(-1, pl.when(pl.col("Label") == "-").then(0).otherwise(1).alias("Labels"))
        return df.drop("Label")

    @staticmethod
    def SL100(df: pl.DataFrame, labels_path: str) -> pl.DataFrame:
        def is_malicious(label: dict) -> bool:
            return bool(label["malicious"])

        def get_timestamp(label: dict) -> str:
            dt = datetime.fromisoformat(label["@timestamp"])
            return dt.timestamp()

        df = df.with_row_index()
        print(df)
        df_2 = df.clone().insert_column(-1, pl.col("Timestamp").cast(float).alias("Time_"))

        labels = op.load_json(labels_path)
        indices = []
        for label in tqdm(
            labels,
            desc="\033[45m  \033[0mAssigning labels to logs ⏳",
            bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
        ):
            if is_malicious(label):
                df_ = df_2.filter(pl.col("Content") == label["message"])
                idx = (df_.with_columns(
                    pl.col("Time_") - get_timestamp(label)
                )["Time_"]).abs().arg_min()
                indices.extend(df_[idx]["index"].to_list())

        indices = list(set(indices))

        df = df.with_columns(
            pl.when(pl.col("index").is_in(indices)).then(1).otherwise(0).alias("Labels")
        )
        df.drop("index")

        return df