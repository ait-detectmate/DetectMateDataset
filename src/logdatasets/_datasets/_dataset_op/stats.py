import polars as pl


class Stats:
    @staticmethod
    def from_df(df: pl.DataFrame, n_memory: str) -> dict:

        found_ratio = 1
        if "Templates" in df and len(df) > 0:
            found_ratio = len(df.filter(pl.col("Templates") != "template not found")) / len(df)

        labels = 0
        if "Labels" in df and len(df) > 0:
            labels = round(df["Labels"].sum() / len(df), 2)
        return {
            "Field": ["Size", "Cache memory", "N. Anomalies", "N. events", "Found ratio"],
            "Values": [
                len(df),
                n_memory,
                f"{labels} %" if "Labels" in df else "0 %",
                df["EventIDs"].unique().len() if "EventIDs" in df else 0,
                f"{round(found_ratio * 100, 2)} %",
            ]
        }

    @staticmethod
    def from_lazy(df: pl.LazyFrame, n_memory: str) -> dict:
        n = df.select(pl.len()).collect().item()
        schema = df.collect_schema()

        found_ratio = 1
        if "Templates" in schema:
            found_ratio = df.filter(
                pl.col("Templates") != "template not found"
            ).select(pl.len()).collect().item() / n

        return {
            "Field": ["Size", "Cache memory", "N. Anomalies", "N. events", "Found ratio"],
            "Values": [
                n,
                n_memory,
                f"{round(df.select(
                    pl.col("Labels").sum()
                ).collect().item() / n, 2)} %" if "Labels" in schema else "0 %",
                df.select(
                    pl.col("EventIDs").unique().len()
                ).collect().item() if "EventIDs" in schema else 0,
                f"{round(found_ratio * 100, 2)} %",
            ]
        }