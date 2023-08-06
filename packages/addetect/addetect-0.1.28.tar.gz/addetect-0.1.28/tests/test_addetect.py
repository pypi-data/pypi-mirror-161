from addetect.detector import Detector
import numpy as np
import pandas as pd
import pytest


@pytest.mark.parametrize(
    "serie, detect_method, output",
    [
        (pd.Series([1, 2, 3, 4]), None, pd.Series([1, 2, 3, 4])),
        (pd.Series([1, 2, 3, 4]), ["test1"], ValueError("The detection method test1 does not exist")),
        ([1, 2, 7, 1000], None, TypeError("The type of the series must be pd.Series"))
    ]
)
def test_init(serie, detect_method, output):
    if isinstance(output, Exception):
        with pytest.raises(output.__class__) as e:
            Detector(serie, detect_method)
        assert str(output) in str(e.value)
    else:
        assert Detector(serie, detect_method).serie.equals(output)


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series([10, 12, 14, 15, 16, 19, 20, 21, 22, 159, 180],
                                   index=pd.date_range(start="2022-01-01", end="2022-01-11"), name="value")),

         pd.Series([159, 180], index=pd.date_range(start="2022-01-10", end="2022-01-11"), name="value")),

        (Detector(series=pd.Series([10, 12, 14, 15, 16],
                                   index=["2022-01-01", "2022-01-02", "2022-01-03", "2022-01-04", "2022-01-05"],
                                   name="value")),
         pd.Series([], index=[], name="value", dtype=int))
    ]
)
def test_iqr(detector, output):
    res = detector._iqr()
    assert res.equals(output)


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), [0.6283741665788453,
                                                                                        0.5788958857458654,
                                                                                        0.5294176049128854,
                                                                                        0.5046784644963954,
                                                                                        0.4799393240799054,
                                                                                        0.4057219028304355,
                                                                                        0.3809827624139455,
                                                                                        0.3562436219974556,
                                                                                        0.33150448158096557,
                                                                                        0.3067653411644756,
                                                                                        0.2820262007479856,
                                                                                        0.2572870603314957,
                                                                                        0.2325479199150057,
                                                                                        0.20780877949851573,
                                                                                        0.18306963908202575,
                                                                                        0.15833049866553578,
                                                                                        0.1335913582490458,
                                                                                        0.3562436219974556,
                                                                                        0.2820262007479856,
                                                                                        0.009895656166595953,
                                                                                        0.08906090549936393,
                                                                                        0.3562436219974556,
                                                                                        0.23749574799830378,
                                                                                        3.0577577554781605,
                                                                                        3.5772797042244497, ])
    ]
)
def test_get_z_score(detector, output):
    j = 0
    for i in detector.serie.values:
        res = detector.get_zscore(i)
        assert res == output[j]
        j += 1


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")),
         pd.Series([159, 180], index=pd.date_range(start="2022-01-24", end="2022-01-25"), name="value"))
    ]
)
def test_z_score(detector, output):
    assert detector._zscore().equals(output)


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")),
         pd.Series([159, 180], index=pd.date_range(start="2022-01-24", end="2022-01-25"), name="value")),

        (Detector(pd.Series([0.047, 0.83, 0.91, 1.03, 0.62], index=pd.date_range(start="2022-02-12", end="2022-02-16"),
                            name="value")), ValueError("The series does not follow a normal law, so we cannot use this "
                                                       "method")
         )
    ]
)
def test_standard_deviation(detector, output):
    if isinstance(output, Exception):
        with pytest.raises(output.__class__) as e:
            detector._standard_deviation()
        assert str(output) in str(e.value)
    else:
        assert detector._standard_deviation().equals(output)


@pytest.mark.parametrize(
    "detector, alpha_level, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), 0.5, True),

        (Detector(pd.Series([0.047, 0.83, 0.91, 1.03, 0.62], index=pd.date_range(start="2022-02-12", end="2022-02-16"),
                            name="value")), 0.05, False)
    ]
)
def test_verif_norm(detector, alpha_level, output):
    assert detector._verif_norm() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), pd.to_datetime('2022-01-01')),
        (Detector(series=pd.Series(
            [np.nan, np.nan, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45,
             159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), pd.to_datetime('2022-01-04')),
        (Detector(series=pd.Series(
            [np.nan, 12, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, np.nan,
             np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), pd.to_datetime('2022-01-02')),

    ]
)
def test_first_date(detector, output):
    assert detector._first_date() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), pd.to_datetime('2022-01-25')),
        (Detector(series=pd.Series(
            [15, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180, np.nan, np.nan, np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-22"), name="value")), pd.to_datetime('2022-01-19')),
        (Detector(series=pd.Series(
            [np.nan, 12, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, np.nan,
             np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), pd.to_datetime('2022-01-23')),

    ]
)
def test_last_date(detector, output):
    assert detector._last_date() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), 25),
        (Detector(series=pd.Series(
            [15, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180, np.nan, np.nan, np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-22"), name="value")), 19),
        (Detector(series=pd.Series(
            [np.nan, 12, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, np.nan,
             np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), 22),
        (Detector(series=pd.Series(
            [np.nan, 12, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 10,
             12],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), 24),

    ]
)
def test_count_date(detector, output):
    assert detector._count_date() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")),
         pd.Series(
             [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
             index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")),

        (Detector(series=pd.Series(
            [15, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180, np.nan, np.nan, np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-22"), name="value")),
         pd.Series(
             [15, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
             index=pd.date_range(start="2022-01-01", end="2022-01-19"), name="value", dtype=float)),

        (Detector(series=pd.Series(
            [np.nan, 12, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, np.nan,
             np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")),
         pd.Series(
             [12, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45],
             index=pd.date_range(start="2022-01-02", end="2022-01-23"), name="value")),

        (Detector(series=pd.Series(
            [np.nan, 12, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 10,
             12],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")),
         pd.Series(
             [12, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 10,
              12],
             index=pd.date_range(start="2022-01-02", end="2022-01-25"), name="value"))

    ]
)
def test_serie_between_first_and_last_index(detector, output):
    assert detector._serie_between_first_and_last_index().equals(output)


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), 0),

        (Detector(series=pd.Series(
            [15, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180, np.nan, np.nan, np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-22"), name="value")), 0),

        (Detector(series=pd.Series(
            [np.nan, 12, np.nan, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, np.nan,
             np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"), name="value")), 1)

    ]
)
def test_count_nan_between_index(detector, output):
    assert detector._count_nan_between_index() == output


@pytest.mark.parametrize(
    "detector, freq, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), "D", True),
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), "B", False),

        (Detector(series=pd.Series(
            [1, 2, 3, 4, 5, 6], index=["2022-01-03", "2022-01-04", "2022-01-05", "2022-01-06", "2022-01-07",
                                       "2022-01-10"])), "B", True),
        (Detector(series=pd.Series(
            [1, 2, 3, 4, 5, 6], index=["2022-01-03", "2022-01-04", "2022-01-05", "2022-01-06", "2022-01-07",
                                       "2022-01-10"])), "D", False)
    ]
)
def test_not_jump_date(detector, freq, output):
    assert detector._not_jump_date(freq=freq) == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), True),

        (Detector(series=pd.Series([1, 2, 3, 4, 5, 6],
                                   index=["2022-01-03", "2022-01-04", "2022-01-04", "2022-01-06", "2022-01-07",
                                          "2022-01-10"])), False)
    ]
)
def test_verif_not_duplicate_index(detector, output):
    assert detector._verif_not_duplicate_index() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 4),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 19, 20, 21, 22, 23, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), -1),

    ]
)
def test_get_minimum(detector, output):
    assert detector._get_minimum() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 180),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 19, 20, 21, 22, 600, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 600),

    ]
)
def test_get_maximum(detector, output):
    assert detector._get_maximum() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 40.845),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 19, 20, 21, 22, 600, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 118.266),

    ]
)
def test_get_standard_deviation(detector, output):
    assert round(detector._get_standard_deviation(), 3) == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 34.56),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 19, 20, 21, 22, 600, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 56.96),

    ]
)
def test_get_mean(detector, output):
    assert round(detector._get_mean(), 3) == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 19.0),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 46, 28, 20, 21, 22, 600, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-26"))), 20.25),

    ]
)
def test_get_first_quantile(detector, output):
    assert detector._get_first_quantile() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 29.0),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 46, 28, 20, 21, 22, 600, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-26"))), 33.75),

    ]
)
def test_get_last_quantile(detector, output):
    assert detector._get_last_quantile() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), 23.0),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 46, 28, 20, 21, 22, 600, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-26"))), 25.0),

    ]
)
def test_get_median(detector, output):
    assert detector._get_median() == output


@pytest.mark.parametrize(
    "detector, type, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21, 22, 23, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-25"))), np.dtype("int64"), True),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 46, 28, 20, 21, 22, 600, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-26"))), float, False),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 46, 28, 20, 21, 22, 600, 24, 4, 26, 27, 28, 29, 30, 21, 24, 35, 39, 21, 45, 159, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-26"))), None, ValueError("The type cannot be null")),

    ]
)
def test_verif_type_of_serie(detector, type, output):
    if isinstance(output, Exception):
        with pytest.raises(output.__class__) as e:
            detector._verif_type_of_serie(kind=type)
        assert str(output) in str(e.value)
    else:
        assert detector._verif_type_of_serie(kind=type) == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"))),

         pd.Series(
             [np.nan, 0.200, 0.167,
              0.071,
              0.067,
              0.188,
              0.053,
              0.050],
             index=pd.date_range(start="2022-01-01", end="2022-01-08"))),

        (Detector(series=pd.Series(
            [24, 4, 26, 27, 28, 2935, 45, 159],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"))),

         pd.Series(
             [np.nan, -0.833,
              5.500,
              0.038,
              0.037,
              103.821,
              -0.985,
              2.533, ],
             index=pd.date_range(start="2022-01-01", end="2022-01-08"))),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 159, 180, np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"))),
         pd.Series(
             [np.nan, 0.200,
              0.167,
              0.071,
              -1.067,
              -160.000,
              0.132, 0],
             index=pd.date_range(start="2022-01-01", end="2022-01-08"))),

    ]
)
def test__variation_between_date(detector, output):
    assert np.round(detector._variation_between_date(), 3).equals(output)


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"))), 0.200),

        (Detector(series=pd.Series(
            [24, 4, 26, 27, 28, 2935, 45, 159],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"))), 103.82),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 159, 180, np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"))), 0.200)

    ]
)
def test_max_variation(detector, output):
    assert np.round(detector._max_variation(), 2) == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [10, 12, 14, 15, 16, 19, 20, 21],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"))), 0.050),

        (Detector(series=pd.Series(
            [24, 4, 26, 27, 28, 2935, 45, 159],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"))), -0.98),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 159, 180, np.nan],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"))), -160.000)

    ]
)
def test_min_variation(detector, output):
    assert np.round(detector._min_variation(), 2) == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [-9, -9, -9, -9, 10, -9, -9, 10, 11, 1, 1, 1, 10, 1, 1, 12, 12, 1, 1, -9],
            index=pd.date_range(start="2022-01-01", end="2022-01-20"), name="values")), 6),

        (Detector(series=pd.Series(
            [24, 4, 26, 27, 28, 2935, 45, 159],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"), name="values")), 0),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 180, np.nan, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"), name="values")), 1)

    ]
)
def test_nb_flat(detector, output):
    assert detector._nb_flat()[0] == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (Detector(series=pd.Series(
            [-9, -9, -9, -9, 10, -9, -9, 10, 11, 1, 1, 1, 10, 1, 1, 12, 12, 1, 1, -9],
            index=pd.date_range(start="2022-01-01", end="2022-01-20"), name="values")), 4),

        (Detector(series=pd.Series(
            [24, 4, 26, 27, 28, 2935, 45, 159],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"), name="values")), 0),

        (Detector(series=pd.Series(
            [10, 12, 14, 15, -1, 180, np.nan, 180],
            index=pd.date_range(start="2022-01-01", end="2022-01-08"), name="values")), 2)

    ]
)
def test__max_len_flat(detector, output):
    assert detector._max_len_flat() == output


@pytest.mark.parametrize(
    "detector, output",
    [
        (
                Detector(series=pd.Series(
                    [-9, -9, -9, -9, 10, -9, -9, 180, 11, 1, 1, 1, 10, 1, 1, 12, 12, 1, 1, -9],
                    index=pd.date_range(start="2022-01-01", end="2022-01-20"), name="values"),
                    detect_methods=["zscore", 'iqr',
                                    "standard_deviation"]),

                [pd.Series([180], index=pd.date_range("2022-01-08", "2022-01-09", inclusive='left'),
                           dtype=np.dtype("int64"), name="values"),
                 pd.Series([180], index=pd.date_range("2022-01-08", "2022-01-09", inclusive='left'),
                           dtype=np.dtype("int64"), name="values"),
                 pd.Series([180], index=pd.date_range("2022-01-08", "2022-01-09", inclusive='left'),
                           dtype=np.dtype("int64"), name="values")]
        )
    ]
)
def test_detect_outliers(detector, output):
    res = detector._detect_outliers()
    for i in range(len(res)):
        assert res[i].equals(output[i])


@pytest.mark.parametrize(
    "detector, maximum, output",
    [
        (Detector(series=pd.Series(
            [-9, -9, -9, -9, 10, -9, -9, 10, 11, 1, 1, 1, 10, 1, 1, 12, 12, 1, 1, -9],
            index=pd.date_range(start="2022-01-01", end="2022-01-20"), name="values")), 3,

         pd.Series(
             [10, 10, 11, 10, 12, 12],
             index=pd.DatetimeIndex(
                 ["2022-01-05", "2022-01-08", "2022-01-09", "2022-01-13", "2022-01-16", "2022-01-17"]), name="values"))

    ]
)
def test_outlier_by_max(detector, maximum, output):
    assert detector._outlier_by_max(maximum).equals(output)


@pytest.mark.parametrize(
    "detector, minimum, output",
    [
        (Detector(series=pd.Series(
            [-9, -9,  10, 10, 11, 1, 1, 1, 10, 1, 1, 12, 12, 1, 1, -5],
            index=pd.date_range(start="2022-01-01", end="2022-01-16"), name="values")), 0,

         pd.Series(
             [-9, -9, -5],
             index=pd.DatetimeIndex(
                 ["2022-01-01", "2022-01-02", "2022-01-16"]), name="values"))

    ]
)
def test_outlier_by_min(detector, minimum, output):
    assert detector._outlier_by_min(minimum).equals(output)
