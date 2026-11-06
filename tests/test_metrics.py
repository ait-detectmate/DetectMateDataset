import logdatasets._metrics as metrics

import polars as pl


def test_add_pred():
    df = pl.DataFrame({"Labels": [1, 0, 0, 1]})
    pred = [True, True, False, False]

    df2 = metrics.add_pred(df, pred=pred)
    expected = pl.DataFrame({
        "Labels": [1, 0, 0, 1],
        "Pred.": ["TP", "FP", "TN", "FN"],
    })

    assert df2.equals(expected)


def test_add_pred_lazy():
    df = pl.LazyFrame({"Labels": [1, 0, 0, 1]})
    pred = [True, True, False, False]

    df2 = metrics.add_pred(df, pred=pred)
    expected = pl.DataFrame({
        "Labels": [1, 0, 0, 1],
        "Pred.": ["TP", "FP", "TN", "FN"],
    })

    assert df2.collect().equals(expected)


def test_add_concat_window():
    df = pl.DataFrame({"Labels": [1, 0, 0, 1], "other": [3, 3, 3, 3]})

    df2 = metrics.concat_by_window(df, window_size=2)
    expected = pl.DataFrame({
        "Labels": [1, 1, 0, 1], "other": [3, 3, 3, 3]
    })

    assert df2.equals(expected)


def test_add_concat_window_lazy():
    df = pl.LazyFrame({"Labels": [1, 0, 0, 1], "other": [3, 3, 3, 3]})

    df2 = metrics.concat_by_window(df, window_size=2)
    expected = pl.DataFrame({
        "Labels": [1, 1, 0, 1], "other": [3, 3, 3, 3]
    })

    assert df2.collect().equals(expected)


def test_n():
    df = pl.DataFrame({"Pred.": ["TP", "TP", "FP", "FP"],})
    assert metrics._Metric.n(df) == 4

    df = pl.DataFrame({"Pred.": ["TP", "TN", "FP", "FN"],})
    assert metrics._Metric.n_p(df) == 2

    df = pl.DataFrame({"Pred.": ["FP", "TN", "FP", "FN"],})
    assert metrics._Metric.n_n(df) == 3


def test_n_lazy():
    df = pl.LazyFrame({"Pred.": ["TP", "TP", "FP", "FP"],})
    assert metrics._Metric.n(df) == 4

    df = pl.LazyFrame({"Pred.": ["TP", "TN", "FP", "FN"],})
    assert metrics._Metric.n_p(df) == 2

    df = pl.LazyFrame({"Pred.": ["FP", "TN", "FP", "FN"],})
    assert metrics._Metric.n_n(df) == 3


def test_tpr():
    df = pl.DataFrame({"Pred.": ["TP", "TP", "FP", "FP"],})
    assert round(metrics._Metric.tpr(df)) == 1.

    df = pl.DataFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    assert round(metrics._Metric.tpr(df), 1) == 0.5

    df = pl.DataFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.tpr(df) == 0.


def test_tpr_lazy():
    df = pl.LazyFrame({"Pred.": ["TP", "TP", "FP", "FP"],})
    assert round(metrics._Metric.tpr(df)) == 1.

    df = pl.LazyFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    assert round(metrics._Metric.tpr(df), 1) == 0.5

    df = pl.LazyFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.tpr(df) == 0.


def test_tnr():
    df = pl.DataFrame({"Pred.": ["TP", "TP", "TN", "TN"],})
    assert round(metrics._Metric.tnr(df)) == 1.

    df = pl.DataFrame({"Pred.": ["TP", "FN", "TN", "FP"],})
    assert round(metrics._Metric.tnr(df), 1) == 0.5

    df = pl.DataFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.tnr(df) == 0.


def test_tnr_lazy():
    df = pl.LazyFrame({"Pred.": ["TP", "TP", "TN", "TN"],})
    assert round(metrics._Metric.tnr(df)) == 1.

    df = pl.LazyFrame({"Pred.": ["TP", "FN", "TN", "FP"],})
    assert round(metrics._Metric.tnr(df), 1) == 0.5

    df = pl.LazyFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.tnr(df) == 0.


def test_balance_accuracy():
    df = pl.DataFrame({"Pred.": ["TP", "TP", "TN", "TN"],})
    assert round(metrics._Metric.balance_accuracy(df)) == 1.

    df = pl.DataFrame({"Pred.": ["TP", "FN", "TN", "FP"],})
    assert round(metrics._Metric.balance_accuracy(df), 1) == 0.5

    df = pl.DataFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.balance_accuracy(df) == 0.


def test_balance_accuracy_lazy():
    df = pl.LazyFrame({"Pred.": ["TP", "TP", "TN", "TN"],})
    assert round(metrics._Metric.balance_accuracy(df)) == 1.

    df = pl.LazyFrame({"Pred.": ["TP", "FN", "TN", "FP"],})
    assert round(metrics._Metric.balance_accuracy(df), 1) == 0.5

    df = pl.LazyFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.balance_accuracy(df) == 0.


def test_f1():
    df = pl.DataFrame({"Pred.": ["TP", "TP", "TN", "TN"],})
    assert round(metrics._Metric.f1(df)) == 1.

    df = pl.DataFrame({"Pred.": ["TP", "FN", "TN", "FP"],})
    assert round(metrics._Metric.f1(df), 1) == 0.5

    df = pl.DataFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.f1(df) == 0.


def test_f1_lazy():
    df = pl.LazyFrame({"Pred.": ["TP", "TP", "TN", "TN"],})
    assert round(metrics._Metric.f1(df)) == 1.

    df = pl.LazyFrame({"Pred.": ["TP", "FN", "TN", "FP"],})
    assert round(metrics._Metric.f1(df), 1) == 0.5

    df = pl.LazyFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.f1(df) == 0.


def test_recall():
    df = pl.DataFrame({"Pred.": ["TP", "TP", "FP", "FP"],})
    assert round(metrics._Metric.recall(df)) == 1.

    df = pl.DataFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    assert round(metrics._Metric.recall(df), 1) == 0.5

    df = pl.DataFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.recall(df) == 0.


def test_recall_interval():
    df = pl.DataFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    (min_, max_) = metrics._Metric.recall_confidence_interval(df)
    assert round(min_, 1) == 0.1
    assert round(max_, 1) == 0.9


def test_recall_lazy():
    df = pl.LazyFrame({"Pred.": ["TP", "TP", "FP", "FP"],})
    assert round(metrics._Metric.recall(df)) == 1.

    df = pl.LazyFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    assert round(metrics._Metric.recall(df), 1) == 0.5

    df = pl.LazyFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.recall(df) == 0.


def test_precision():
    df = pl.DataFrame({"Pred.": ["TP", "TN", "FP", "FP"],})
    assert metrics._Metric.precision(df) == 0.3333333333222222

    df = pl.DataFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    assert metrics._Metric.precision(df) == 0.3333333333222222

    df = pl.DataFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.precision(df) == 0.0


def test_precision_interval():
    df = pl.DataFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    (min_, max_) = metrics._Metric.precision_confidence_interval(df)
    assert round(min_, 1) == 0.1
    assert round(max_, 1) == 0.8


def test_precision_lazy():
    df = pl.LazyFrame({"Pred.": ["TP", "TN", "FP", "FP"],})
    assert metrics._Metric.precision(df) == 0.3333333333222222

    df = pl.LazyFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    assert metrics._Metric.precision(df) == 0.3333333333222222

    df = pl.LazyFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.precision(df) == 0.0


def test_jaccard():
    df = pl.DataFrame({"Pred.": ["TP", "TN", "FP", "FP"],})
    assert metrics._Metric.jaccard_index(df) == 0.3333333333222222

    df = pl.DataFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    assert round(metrics._Metric.jaccard_index(df), 2) == 0.25

    df = pl.DataFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.jaccard_index(df) == 0.0


def test_jaccard_lazy():
    df = pl.LazyFrame({"Pred.": ["TP", "TN", "FP", "FP"],})
    assert metrics._Metric.jaccard_index(df) == 0.3333333333222222

    df = pl.LazyFrame({"Pred.": ["TP", "FN", "FP", "FP"],})
    assert round(metrics._Metric.jaccard_index(df), 2) == 0.25

    df = pl.LazyFrame({"Pred.": ["FN", "FN", "FP", "FP"],})
    assert metrics._Metric.jaccard_index(df) == 0.0

def test_get_metrics_scores_labels_only(monkeypatch):
    # The counts filter the frame; on an eager frame every column of the matching rows is
    # copied, which pushed HDFS past the memory cap. Only Labels is needed.
    import logdatasets._datasets.dataset as dataset_mod

    seen = []
    monkeypatch.setattr(dataset_mod, "do_metrics", lambda df, pred, **kw: seen.append((df, pred)))
    for frame in (pl.DataFrame, pl.LazyFrame):
        seen.clear()
        ds = dataset_mod.Dataset("t", frame({"Content": ["a", "b", "c", "d"], "Labels": [1, 0, 0, 1]}))
        ds.get_metrics([True, True, False, False], do_print=False, skip=1)
        df, pred = seen[0]
        assert df.collect_schema().names() == ["Labels"]
        df = df.collect() if isinstance(df, pl.LazyFrame) else df
        assert df["Labels"].to_list() == [0, 0, 1]
        assert pred == [True, False, False]
