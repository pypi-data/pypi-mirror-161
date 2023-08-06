import datetime
from typing import List, Optional, Tuple, Hashable
from scipy import stats
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.preprocessing import StandardScaler
# from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class Detector:
    DETEC_METHOD = [
        "standard_deviation",
        "iqr",
        "zscore",
    ]

    def __init__(
            self,
            series: Optional[pd.Series] = None,
            detect_methods: Optional[List[str]] = None,
    ):
        """
        The constructor of the Detector class.

        Parameters
        ----------
        series : pd.Series
            If None, will have to be specified later by setting the instance's 'series' attribute.
        detect_methods : List[str]
            If None, will default to 'standard_deviation'.

        Raises
        ---------
        TypeError
            If 'series' is not a pd.Series object.
        ValueError
            If any of the detection methods is unknown by the class.
        """

        if not isinstance(series, pd.Series):
            raise TypeError(f"The type of the series must be pd.Series and not {type(series)}")
        self._serie = series
        if detect_methods is not None:
            for d_meth in detect_methods:
                if d_meth not in self.DETEC_METHOD:
                    raise ValueError(f"The detection method {d_meth} does not exist in {self.DETEC_METHOD}")
        if detect_methods is None:
            self._detect_method = ["standard_deviation"]
        else:
            self._detect_method = detect_methods

    @property
    def serie(self) -> pd.Series:
        """
        Series is the timesseries for which we want to find the outliers.
        """
        return self._serie

    @serie.setter
    def serie(self, values: pd.Series):
        if not isinstance(values, pd.Series):
            raise TypeError(f"The type of the series must be pd.Series and not {type(values)}")
        self._serie = values

    @property
    def detect_method(self) -> List[str]:
        """
        "detect_method" is the list containing the detect methods with which we want to find the outliers.
        """
        return self._detect_method

    def get_zscore(self, value) -> int:
        """
        Computes the zscore of "value". ("value" corresponding to a value of self._serie).

        Parameters
        ----------
        value : int
            The value whose zscore is desired.
        Returns
        -------
        int
            zscore of value.
        """
        mean = np.mean(self.serie)
        std = np.std(self.serie)
        z_score = (value - mean) / std
        return np.abs(z_score)

    def _verif_norm(self, alpha_level=0.05):
        """
        This method checks if the series follows a normal distribution.

        Parameters
        ----------
        alpha_level : float
            the probability of making the wrong decision.

        Returns
        -------
        bool
            True if p-value < alpha_lever
            False else
        """
        series = self.serie.dropna()
        df_res = pd.DataFrame(series)
        ks = stats.ks_1samp(series, stats.norm.cdf)
        df_res.loc["p-value", series.name] = ks.pvalue
        if df_res.loc["p-value", series.name] < alpha_level:
            return True
        else:
            return False

    def _zscore(self) -> pd.Series:
        """
        This method detects outliers from the z_score.

        Returns
        -------
        pd.Series
            outliers is a series containing date and value of outliers.
        """
        series = self.serie.dropna()
        res = pd.DataFrame(series)
        res["z-score"] = series.apply(lambda x: self.get_zscore(x))
        res = res[res["z-score"] > 3]
        outliers = res[series.name]
        return outliers

    def _iqr(self) -> pd.Series:
        """
        This method entails using the 1st quartile, 3rd quartile, and IQR to define the lower bound and upper bound
        for the data points.

        Returns
        -------
        pd.Series
            outliers is a series containing date and value of outliers
        """
        series = self.serie.dropna()
        quantile_1 = np.quantile(series, 0.25)
        quantile_3 = np.quantile(series, 0.75)
        iqr = quantile_3 - quantile_1
        lower_bound = quantile_1 - 1.5 * iqr
        upper_bound = quantile_3 + 1.5 * iqr

        outliers = series[(series < lower_bound) | (series > upper_bound)]
        return outliers

    def _standard_deviation(self) -> pd.Series:
        """
        This method find the outliers with the standard deviation

        Returns
        -------
        pd.Series
            outliers is a series containing date and value of outliers
        Raises
        -------
            ValueError
        """
        if self._verif_norm() is False:
            raise ValueError("The series does not follow a normal law, so we cannot use this method")
        series = self.serie.dropna()
        mean, std = np.mean(series), np.std(series)
        cut_off = std * 3
        lower, upper = mean - cut_off, mean + cut_off
        outliers = series[(series < lower) | (series > upper)]

        return outliers

    def _outlier_by_max(self, maximum) -> pd.Series:
        """
        This method find the outliers higher than the maximum

        Parameters
        ----------
        maximum : int
            The maximum value

        Returns
        -------
        pd.Series
            The serie with the outliers
        """
        series = self.serie.dropna()
        df_res = pd.DataFrame(series)
        series = series[df_res[series.name] > maximum]
        return series

    def _outlier_by_min(self, minimum) -> pd.Series:
        """
        This method find the outliers higher than the minimum

        Parameters
        ----------
        minimum : int
            The minimum value

        Returns
        -------
        pd.Series
            The serie with the outliers
        """
        series = self.serie.dropna()
        df_res = pd.DataFrame(series)
        series = series[df_res[series.name] < minimum]
        return series

    # def _isolation_forest(self, outlier_fraction=.01) -> pd.Series:
    #     """
    #     The isolation forest attempts to separate each point from the data. In the case of 2D,
    #     it randomly creates a line
    #     and tries to isolate a point. In this case, an abnormal point can be separated in a few steps, while normal
    #     points that are closer together may take many more steps to separate.
    #
    #     Returns
    #     -------
    #     pd.Series
    #         Series containing the outliers
    #     """
    #     scaler = StandardScaler()
    #     serie = self.serie.dropna()
    #     df_res = pd.DataFrame(serie)
    #     np_scaled = scaler.fit_transform(serie.values.reshape(-1, 1))
    #     data = pd.DataFrame(np_scaled)
    #     model = IsolationForest(contamination=outlier_fraction)
    #     model.fit(data)
    #     df_res['anomaly'] = model.predict(data)
    #     a = df_res.loc[df_res['anomaly'] == -1, [serie.name]]  # anomaly
    #     print(a)
    #     return a

    # # TODO : not finish to improve
    # def _arima(self):
    #     """
    #     Find outliers with arima method.
    #
    #     Returns
    #     -------
    #     pd.Series
    #         Outliers
    #     """
    #
    #     def test_stationarity(ts_data, signif=0.05):
    #         adf_test = adfuller(ts_data, autolag='AIC')
    #         p_value = adf_test[1]
    #         if p_value <= signif:
    #             test_result = "Stationary"
    #         else:
    #             test_result = "Non-Stationary"
    #         return test_result
    #
    #     def find_anomalies(squared_errors):
    #         threshold = np.mean(squared_errors) + np.std(squared_errors)
    #         predictions = (squared_errors >= threshold).astype(int)
    #         return predictions, threshold
    #
    #     if test_stationarity(self.serie.dropna()) != "Stationary":
    #         raise TypeError("Your series is not stationary, so this method cannot be applied")
    #
    #     serie = self.serie.dropna()
    #     arma = ARIMA(serie, order=(0, 0, 0))
    #     arma_fit = arma.fit()
    #     squared_errors = arma_fit.resid ** 2
    #     predictions, threshold = find_anomalies(squared_errors)
    #     data = pd.DataFrame(serie)
    #     data['predictions'] = predictions
    #     data = data.loc[data["predictions"] == 1, self.serie.name]
    #     return data

    def _detect_outliers(self) -> List[list]:
        """
        This method detects outliers based on self._detetct_method.

        Returns
        -------
        list
            list containing the outliers according to the different method.
        """
        output = []
        for m in self.detect_method:
            output.append(getattr(self, f"_{m}")())
        return output

    def _first_date(self):
        """
        This method finds the first non-null date.

        Returns
        -------
        datetime
            The first non-null date
        """
        return self.serie.first_valid_index()

    def _last_date(self):
        """
        This method finds the last non-null date.

        Returns
        -------
        datetime
            The last index non-null date.
        """
        return self.serie.last_valid_index()

    def _count_date(self) -> int:
        """
        Count the number of dates from the first to the last non-null index

        Returns
        -------
        int
            Number of date
        """

        return len(self.serie.loc[self._first_date():self._last_date()])

    def _serie_between_first_and_last_index(self) -> pd.Series:
        """
        Get the serie between the first and last date non-null.

        Returns
        -------
        pd.Series
            The serie between the first and last non-null date.
        """
        return self.serie.loc[self._first_date():self._last_date()]

    def _count_nan_between_index(self) -> int:
        """
        Count the number of nan between the first and last index

        Returns
        -------
        int
            number of nan
        """
        return self.serie.loc[self._first_date():self._last_date()].isna().sum()

    def _not_jump_date(self, freq="B") -> bool:
        """
        Check that no dates are missing according to the frequency

        Returns
        -------
        bool
            True If there are missing dates
            False else

        """
        return len(pd.date_range(start=self._first_date(), end=self._last_date(), freq=freq)) == len(
            self._serie_between_first_and_last_index())

    def _verif_not_duplicate_index(self) -> bool:
        """
        Check that there are no duplicate indexes.

        Returns
        -------
        True If there is no
        False else

        """
        return self.serie.index.duplicated().sum() == 0

    def _get_minimum(self) -> float:
        """
        Get the minimum of the serie.

        Returns
        -------
        float
            The minimum of the serie
        """
        return min(self.serie)

    def _get_maximum(self) -> float:
        """
        Get the maximum of the serie.

        Returns
        -------
        float
            The maximum of the serie
        """
        return max(self.serie)

    def _get_standard_deviation(self) -> float:
        """
        Get the standard deviation of the serie.

        Returns
        -------
        float
            The standard deviation of the serie
        """
        return float(np.std(self.serie))

    def _get_mean(self) -> float:
        """
        Get the standard deviation of the serie.

        Returns
        -------
        float
            The standard deviation of the serie
        """
        return float(np.mean(self.serie))

    def _get_first_quantile(self) -> float:
        """
        Get the first quantile of the serie.

        Returns
        -------
        float
            The first quantile

        """
        return np.quantile(self.serie.dropna(), 0.25)

    def _get_last_quantile(self) -> float:
        """
        Get the first quantile of the serie.

        Returns
        -------
        float
            The last quantile

        """
        return np.quantile(self.serie.dropna(), 0.75)

    def _get_median(self) -> float:
        """
        Get the median of the serie.

        Returns
        -------
        float
            median of serie
        """
        return float(np.median(self.serie.dropna()))

    def _verif_type_of_serie(self, kind) -> bool:
        """
        Check that the data type of our series matches the one in parameter

        Return
        -------
        bool
            true if type corresponding
            false else
        """

        if kind is None:
            raise ValueError("The type cannot be null")
        return self.serie.dtypes is kind

    def _variation_between_date(self) -> pd.Series:
        """
        Get the serie with the pct change.

        Return
        -------
        pd.Series
            The serie with the pct change for each value
        """
        return self.serie.pct_change()

    def _max_variation(self) -> float:
        """
        Get the max variation after pct_change

        Return
        -------
        int
            max of pct_change
        """

        return max(self._variation_between_date().dropna())

    def _min_variation(self) -> float:
        """
        Get the min variation after pct_change

        Return
        -------
        int
            min of pct_change
        """

        return min(self._variation_between_date().dropna())

    def _nb_flat(self) -> Tuple[int, pd.DataFrame]:
        """
        Calculate the number of times there are flat values.

        Return
        -------
        int
            The number of flat
        pd.Dataframe
            The dataframe with the flat
        """
        df_change = self.serie.dropna().pct_change()
        df_change.columns = [self.serie.name]
        df_change = pd.DataFrame(df_change)
        df_change['flat'] = (df_change[self.serie.name] != df_change[self.serie.name].shift(1)).cumsum()
        df_change = df_change[df_change[self.serie.name] == 0].groupby('flat', as_index=False).count()
        return len(df_change[self.serie.name]), df_change[self.serie.name]

    def _max_len_flat(self) -> int:
        """
        Compute the longest flat

        Return
        -------
        int
            The longest flat
        """
        if (self._nb_flat()[1]).empty:
            return 0
        else:
            return max(self._nb_flat()[1]) + 1

    def _plot_with_outliers(self, outliers: pd.Series, show: bool = False):
        """
        The graph of the data as a plot, and the outliers as a scatter.
        Parameters
        ----------
        outliers : pd.Serie
            The serie of outliers
        """
        series = self.serie.dropna()
        plt.figure(figsize=(20, 10))
        plt.xlabel("Date")
        plt.ylabel(series.name)
        plt.plot(pd.DatetimeIndex(series.index), series.values)
        plt.scatter(pd.DatetimeIndex(outliers.index), outliers.values, c="red")
        plt.savefig("plot/plot")
        if show:
            plt.show()
