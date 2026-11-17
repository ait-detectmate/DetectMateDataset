import polars as pl
from numpy import zeros


import warnings


class PostProcess:
    @staticmethod
    def OpenVPN(df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns(
            pl.concat_str([pl.col("Date"), pl.col("Time")], separator=" ")
            .str.to_datetime("%Y-%m-%d %H:%M:%S").cast(float).cast(str)
            .alias("Timestamp")
        )
        return df.drop(["Date", "Time"])

    @staticmethod
    def Audit(df: pl.DataFrame) -> pl.DataFrame:
        return df.rename({"Time": "Timestamp"})

    @staticmethod
    def Apache(df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns(pl.col("Time").str.to_datetime("%d/%b/%Y:%H:%M:%S %z").cast(float).cast(str))
        df.insert_column(df.shape[-1], pl.Series("Content", ["" for _ in range(len(df))]))
        df.insert_column(df.shape[-1], pl.Series("Templates", ["" for _ in range(len(df))]))
        df.insert_column(df.shape[-1], pl.Series("EventIDs", zeros(len(df)).astype(int)))
        df.insert_column(df.shape[-1], pl.Series("ParamList", [[""] for _ in range(len(df))]))

        return df.rename({"Time": "Timestamp"})

    @staticmethod
    def DNSmasq(df: pl.DataFrame) -> pl.DataFrame:
        df = df.insert_column(df.shape[-1], pl.Series("Year", ["2022" for _ in range(len(df))]))
        df = df.with_columns(
            pl.concat_str([pl.col("Year"), pl.col("Month"), pl.col("Day"), pl.col("Time")], separator=" ")
            .str.to_datetime("%Y %b %d %H:%M:%S", strict=False).cast(float).cast(str)
            .alias("Timestamp")
        )

        shape = df.shape[0]
        df = df.drop_nulls("Timestamp")

        if shape != df.shape[0]:
            warnings.warn(
                f"'\033[43mNull timestamp found, drop rate of {(1 - (df.shape[0] / shape)) * 100:.2f} %\033[0m"
            )
        return df.drop(["Year", "Month", "Day", "Time"])

    @staticmethod
    def SysLog(df: pl.DataFrame) -> pl.DataFrame:
        return PostProcess.DNSmasq(df)

    @staticmethod
    def BGL(df: pl.DataFrame) -> pl.DataFrame:
        return df.drop(["Date", "Time", "NodeRepeat"])

    @staticmethod
    def HDFS(df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns(
            pl.concat_str([pl.col("Date"), pl.col("Time")], separator=" ")
            .str.to_datetime("%y%m%d %H%M%S", strict=False).cast(float).cast(str)
            .alias("Timestamp")
        )
        shape = df.shape[0]
        df = df.drop_nulls("Timestamp")

        if shape != df.shape[0]:
            warnings.warn(
                f"'\033[43mNull timestamp found, drop rate of {(1 - (df.shape[0] / shape)) * 100:.2f} %\033[0m"
            )
        return df.drop(["Date", "Time"])

    @staticmethod
    def DroneSL100(df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            pl.concat_str([pl.col("Date"), pl.col("Time")], separator=" ")
            .str.to_datetime("%Y-%m-%d %H:%M:%S")
            .dt.timestamp()
            .alias("Timestamp")
        )