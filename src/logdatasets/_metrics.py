from tabulate import tabulate
from typing import overload
import polars as pl

from scipy.stats import norm
import math


def wilson_score_interval(
    successes: int, total: int, confidence: float = 0.99
) -> tuple[float, float]:
    
    if total == 0:
        return 0.0, 0.0
    
    p = successes / total
    z = norm.ppf(1 - (1 - confidence) / 2)
    
    denominator = 1 + (z**2 / total)
    centre_adjusted_probability = p + (z**2 / (2 * total))
    adjusted_variance = z * math.sqrt((p * (1 - p) / total) + (z**2 / (4 * total**2)))
    
    lower = (centre_adjusted_probability - adjusted_variance) / denominator
    upper = (centre_adjusted_probability + adjusted_variance) / denominator

    return float(max(0.0, lower)), float(min(1.0, upper))


class PredCond:
    TP = "TP"
    FN = "FN"
    FP = "FP"
    TN = "TN"


class _Metric:
    @staticmethod
    def n(df: pl.DataFrame | pl.LazyFrame) -> int:
        return df.shape[0] if isinstance(df, pl.DataFrame) else df.select(pl.len()).collect().item()
    
    @staticmethod
    def n_p(df: pl.DataFrame | pl.LazyFrame) -> int:
        return _Metric.n(df.filter(
            (pl.col("Pred.") == PredCond.TP) | (pl.col("Pred.") == PredCond.FN)
        ))

    @staticmethod
    def n_n(df: pl.DataFrame | pl.LazyFrame) -> int:
        return _Metric.n(df.filter(
            (pl.col("Pred.") == PredCond.TN) | (pl.col("Pred.") == PredCond.FP)
        ))

    @staticmethod
    def n_tp(df: pl.DataFrame | pl.LazyFrame) -> int:
        return _Metric.n(df.filter(pl.col("Pred.") == PredCond.TP))

    @staticmethod
    def n_fn(df: pl.DataFrame | pl.LazyFrame) -> int:
        return _Metric.n(df.filter(pl.col("Pred.") == PredCond.FN))

    @staticmethod
    def n_tn(df: pl.DataFrame | pl.LazyFrame) -> int:
        return _Metric.n(df.filter(pl.col("Pred.") == PredCond.TN))

    @staticmethod
    def n_fp(df: pl.DataFrame | pl.LazyFrame) -> int:
        return _Metric.n(df.filter(pl.col("Pred.") == PredCond.FP))
    @staticmethod
    def tpr(df: pl.DataFrame | pl.LazyFrame) -> float:
        return _Metric.n_tp(df) / (_Metric.n_tp(df) + _Metric.n_fn(df) + 1e-10)
    
    @staticmethod
    def tnr(df: pl.DataFrame | pl.LazyFrame) -> float:
        return _Metric.n_tn(df) / (_Metric.n_tn(df) + _Metric.n_fp(df) + 1e-10)
    
    @staticmethod 
    def balance_accuracy(df: pl.DataFrame | pl.LazyFrame) -> float:
        return (_Metric.tpr(df) + _Metric.tnr(df)) / 2
    
    @staticmethod
    def f1(df: pl.DataFrame | pl.LazyFrame) -> float:
        tp2 = 2 * _Metric.n_tp(df)
        return tp2 / (tp2 + _Metric.n_fp(df) + _Metric.n_fn(df) + 1e-10)
    
    @staticmethod
    def recall(df: pl.DataFrame | pl.LazyFrame) -> float:
        return _Metric.tpr(df)
    
    @staticmethod
    def recall_confidence_interval(
        df: pl.DataFrame | pl.LazyFrame, confidence: float = 0.95
    ) -> tuple[float, float]:
        return wilson_score_interval(
            successes=(tp := _Metric.n_tp(df)), total=tp + _Metric.n_fn(df), confidence=confidence
        )
    
    @staticmethod
    def precision(df: pl.DataFrame | pl.LazyFrame) -> float:
        tp = _Metric.n_tp(df)
        return tp / (tp + _Metric.n_fp(df) + 1e-10)
    
    @staticmethod
    def precision_confidence_interval(
        df: pl.DataFrame | pl.LazyFrame, confidence: float = 0.95
    ) -> tuple[float, float]:
        return wilson_score_interval(
            successes=(tp := _Metric.n_tp(df)), total=tp + _Metric.n_fp(df), confidence=confidence
        )
    
    @staticmethod
    def jaccard_index(df: pl.DataFrame | pl.LazyFrame) -> float:
        tp = _Metric.n_tp(df)
        return tp / (tp + _Metric.n_fn(df) + _Metric.n_fp(df) + 1e-10)


@overload
def add_pred(df: pl.DataFrame, pred: list[bool], col_label: str = "Labels") -> pl.DataFrame:
    ...


@overload
def add_pred(df: pl.LazyFrame, pred: list[bool], col_label: str = "Labels") -> pl.LazyFrame:
    ...


def add_pred(
    df: pl.DataFrame | pl.LazyFrame, pred: list[bool], col_label: str = "Labels"
) -> pl.DataFrame | pl.LazyFrame:
    
    return df.clone().with_columns(pl.Series("a", pred)).with_columns( 
        pl.when(pl.col(col_label) == 1).then(
            pl.when(pl.col("a") == 1).then(pl.lit(PredCond.TP)).otherwise(pl.lit(PredCond.FN))     
        ).otherwise(
            pl.when(pl.col("a") == 1).then(pl.lit(PredCond.FP)).otherwise(pl.lit(PredCond.TN))
        ).alias("Pred.")
    ).drop("a")


@overload
def concat_by_window(df: pl.DataFrame, window_size: int, col_label: str = "Labels") -> pl.DataFrame:
    ...


@overload
def concat_by_window(df: pl.LazyFrame, window_size: int, col_label: str = "Labels") -> pl.LazyFrame:
    ...


def concat_by_window(
    df: pl.DataFrame | pl.LazyFrame, window_size: int, col_label: str = "Labels"
) -> pl.DataFrame | pl.LazyFrame:
    
    return df.with_columns(pl.col(col_label).rolling_sum(window_size=window_size, min_samples=1))


def metrics_calc(
    df: pl.DataFrame | pl.LazyFrame, 
    pred: list[bool], 
    col_label: str = "Labels", 
    window_size: int = 1,
    confidence: float = 0.95,
) -> dict:
    
    df = add_pred(df, pred=pred, col_label=col_label)
    if window_size > 1:
        df = concat_by_window(df, window_size=window_size, col_label=col_label)

    prec_inter = _Metric.precision_confidence_interval(df, confidence=confidence)
    rec_inter = _Metric.recall_confidence_interval(df, confidence=confidence)

    return {
        "Quantity": {
            "N. Elements": _Metric.n(df),
            "N. Positives": _Metric.n_p(df),
            "N. Negatives": _Metric.n_n(df),
        },
        "Raw predictions": {
            "TP": _Metric.n_tp(df),
            "TN": _Metric.n_tn(df),
            "FP": _Metric.n_fp(df),
            "FN": _Metric.n_fn(df),
        },
        "Main metrics": {
            "F1": round(_Metric.f1(df), 2),
            "Balance accuracy": round(_Metric.balance_accuracy(df), 2),
            "Recall": round(_Metric.recall(df), 2),
            "Precision": round(_Metric.precision(df), 2),
            "Jaccard Index": round(_Metric.jaccard_index(df), 2),
        },
        "Confidence Intervals": {
            "Recall conf. min": round(rec_inter[0], 2),
            "Recall conf. max": round(rec_inter[1], 2),
            "Precision conf. min": round(prec_inter[0], 2), 
            "Precision conf. max": round(prec_inter[1], 2),
        },
    }


def do_metrics(
    df: pl.DataFrame | pl.LazyFrame, 
    pred: list[bool], 
    col_label: str = "Labels", 
    do_print: bool = True,
    window_size: int = 1,
    confidence: float = 0.95,
) -> dict:
    
    results = metrics_calc(
        df=df, pred=pred, col_label=col_label, window_size=window_size, confidence=confidence
    )

    if do_print:
        print("\n\033[46m Results    \033[0m")
        print("\033[46m" + "".join([" " for _ in range(100)]) + "\033[0m\n")

        for type_ in results:
            print("\033[4m" + type_ + "\033[0m\n")
            print(tabulate(
                {k:[v] for k,v in results[type_].items()}, 
                headers=results[type_].keys(),
                tablefmt="double_outline"
            ))
            print("\n")

        print("\033[46m" + "".join([" " for _ in range(100)]) + "\033[0m")

    return results