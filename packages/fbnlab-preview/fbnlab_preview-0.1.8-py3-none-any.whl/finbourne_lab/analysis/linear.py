from __future__ import annotations

from typing import Optional
from typing import Union, List

import numpy as np
import pandas as pd
import statsmodels.api as sm
from pandas import DataFrame
from statsmodels.regression.quantile_regression import QuantReg
import matplotlib.pyplot as plt

_cms_scheme = {
    'scatter_plot': {'color': 'black', 'alpha': 0.5},
    'median_line': {'color': 'black', 'ls': '--', 'lw': 2},
    'outer_band': {'color': 'lime', 'alpha': 1.0},
    'inner_band': {'color': 'yellow', 'alpha': 1.0},
}


def _make_monochrome_scheme(c):
    return {
        'scatter_plot': {'color': c, 'alpha': 0.667},
        'median_line': {'color': c, 'ls': '--', 'lw': 2},
        'outer_band': {'color': c, 'alpha': 1 / 6},
        'inner_band': {'color': c, 'alpha': 1 / 3},
    }


class ScalingModel:
    """This class encapsulates the analysis of how an attribute of an experiment scales with a single input value.

    It consists of a set of quantile regressions that put bounds on the scaling behaviour alongside helper methods
    for plotting this relationship, getting its parameters and predicting its values.

    """

    def __init__(self, data: DataFrame, x: str, y: str, name: str):
        """The constructor method of the scaling model.

        Args:
            data (DataFrame): dataframe from an experimental run.
            x (str): the independent variable column name in the dataframe.
            y (str): the dependent variable column name in the dataframe.
            name (str): the name of the model
        """

        if len(data) == 0:
            raise ValueError('The model input dataframe was empty.')

        if 'errored' in data.columns:
            data = data[(~data.errored)]
        if 'force_stopped' in data.columns:
            data = data[(~data.force_stopped)]

        self.data = data.copy()

        if self.data.shape[0] == 0:
            raise ValueError(f"There was no non-errored data to use from the experiment {data.iloc[0].ExperimentName}!")

        self.x = x
        self.y = y
        self.name = name

        model = QuantReg(
            self.data[self.y],
            sm.add_constant(self.data[self.x])
        )

        quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]
        self.fits = {q: model.fit(q) for q in quantiles}

    def predict(self, x: Union[float, List[float], np.array]) -> DataFrame:
        """Predict the 5th, 25th, 50th, 75th and 95th percentiles for given values of the experiment input value.

        Args:
            x (Union[float, List[float], np.array]): a single input value, or array of values, to predict for.

        Returns:
            DataFrame: a dataframe with a row for each value of x and a column for each percentile.
        """
        output = {}

        for q, m in self.fits.items():
            if isinstance(x, (float, int)):
                _x = np.asarray([x, 0]).reshape(-1, 1)
                _x = sm.add_constant(_x)
                output[q] = m.predict(_x)[0]
            elif len(x) == 1:
                _x = np.asarray([x[0], 0]).reshape(-1, 1)
                _x = sm.add_constant(_x)
                output[q] = m.predict(_x)[0]
            else:
                _x = np.asarray(x)
                _x = sm.add_constant(_x)
                output[q] = m.predict(_x)

        if isinstance(x, (float, int)) or len(x) == 1:
            ex_df = DataFrame([output])
        else:
            ex_df = DataFrame(output)

        ex_df['x'] = x
        ex_df = ex_df.set_index('x')
        return ex_df

    def fit_results(self) -> DataFrame:
        """Returns a summary dataframe containing the parameters, p values and std errors for each quantile regression
        line in the model.

        Returns:
            DataFrame: data frame with the fit results.
        """
        rows = []
        for q, m in self.fits.items():
            m.conf_int()
            rows.append({
                'quantile': q,
                'c': m.params[0],
                'm': m.params[1],
                'c_stderr': m.bse[0],
                'm_stderr': m.bse[1],
            })

        fr_df = DataFrame(rows).set_index('quantile')
        fr_df['c_frac_err'] = fr_df['c_stderr'] / fr_df['c']
        fr_df['m_frac_err'] = fr_df['m_stderr'] / fr_df['m']
        return fr_df

    def outliers(self) -> DataFrame:
        """Get lines in the input data that might be outliers according to the fit model.

        Data points are flagged as outliers if they are above the upper quartile + 1.5 * the interquartile range (IQR)
        or are below the lower quartile - 1.5 * IQR.

        Returns:
            DataFrame: dataframe of rows in the input data that may be outliers.
        """
        odf = self.predict(self.data[self.x].values).reset_index()
        odf['IQR'] = odf[0.75] - odf[0.25]
        odf['y'] = self.data[self.y].values
        odf['execution_id'] = self.data['execution_id'].values
        odf = odf[(odf['y'] > odf[0.75] + 1.5 * odf['IQR']) | (odf['y'] < odf[0.25] - 1.5 * odf['IQR'])]
        return self.data[self.data.execution_id.isin(odf.execution_id.tolist())]

    def add_plot(self, ax, color_scheme: Optional[str] = 'cms', show_datapoints: Optional[bool] = True):

        """Add a plot of this scaling model's quantile bands, its median line and the data points that the model was
        fit with to a matplotlib axes object.

        Args:
            ax: the matplotlib axes to draw the plot on.
            color_scheme (str): the color scheme to use. This can be either 'cms' (for a CERN CMS-style brazil band) or
            any valid matplotlib named color.
            show_datapoints (bool): show the observed datapoints. Set to false if a comparison plot's getting too busy.

        """
        if color_scheme == 'cms':
            scheme = _cms_scheme
        else:
            scheme = _make_monochrome_scheme(color_scheme)

        if show_datapoints:
            ax.scatter(
                self.data[self.x],
                self.data[self.y],
                s=10, zorder=99,
                label=f'Observation ({self.name})',
                **scheme['scatter_plot']
            )

        x_min = self.data[self.x].min()
        x_max = self.data[self.x].max()

        x = np.linspace(x_min, x_max, 3)
        pred = self.predict(x)

        ax.plot(x, pred[0.5], label=f'Median ({self.name})', **scheme['median_line'])
        ax.fill_between(x, pred[0.25], pred[0.75], label=f'p25-p75 Range ({self.name})', **scheme['inner_band'])
        ax.fill_between(x, pred[0.75], pred[0.95], label=f'p5-p95 Range ({self.name})', **scheme['outer_band'])
        ax.fill_between(x, pred[0.05], pred[0.25], **scheme['outer_band'])

    def remove_outliers(self) -> ScalingModel:
        """Fit a model, remove outliers from the input data and then fit a new model.

        Returns:
            ScalingModel: a new scaling model fit to data with outliers removed
        """
        outliers = self.outliers()
        data = self.data[~self.data.execution_id.isin(outliers.execution_id)].copy()
        return ScalingModel(data, self.x, self.y, self.name)

    def show(self):
        """Generate and show a single plot of this relationship

        """
        f, ax = plt.subplots(figsize=(12, 7))
        self.add_plot(ax)
        plt.xlabel(self.x)
        plt.ylabel(self.y)
        plt.legend()
        plt.grid(True, ls=':', zorder=-99)
        plt.show()

    def __sub__(self, other: ScalingModel) -> ScalingModel:

        x = self.data[self.x].values
        y = self.data[self.y].values
        y_pred = other.predict(x)[0.5].values
        delta = y - y_pred

        df = self.data
        r = np.random.randint(1000)
        label = f'_delta_{r}'
        df[label] = delta

        return ScalingModel(df, self.x, label, f'{self.name} - {other.name}')

    def __add__(self, other: ScalingModel) -> ScalingModel:

        x = self.data[self.x].values
        y = self.data[self.y].values
        total = y + other.predict(x)[0.5].values

        df = self.data
        r = np.random.randint(1000)
        label = f'_total_{r}'
        df[label] = total

        return ScalingModel(df, self.x, label, f'{self.name} + {other.name}')

    def __truediv__(self, other: ScalingModel) -> ScalingModel:

        x = self.data[self.x].values
        y = self.data[self.y].values
        ratio = y / other.predict(x)[0.5].values

        df = self.data
        r = np.random.randint(1000)
        label = f'_div_{r}'
        df[label] = ratio

        return ScalingModel(df, self.x, label, f'{self.name} / {other.name}')

    def __mul__(self, other: ScalingModel) -> ScalingModel:

        x = self.data[self.x].values
        y = self.data[self.y].values
        y_pred = other.predict(x)[0.5].values
        prod = y * y_pred

        df = self.data
        r = np.random.randint(1000)
        label = f'_prod_{r}'
        df[label] = prod

        return ScalingModel(df, self.x, label, f'{self.name} * {other.name}')

    def merge(self, other, name=None):
        """Merge the underlying data of two linear scaling models together and re-fit

        Args:
            other (ScalingModel): the other model
            name (str): name to give the result of the merge

        Returns:
            ScalingModel: the new scaling model from the merged data
        """

        if self.x != other.x or self.y != other.y:
            raise ValueError(
                f'x and y must match when merging models but were different. '
                f'x: {self.x} vs {other.x}, y: {self.y} vs {other.y}'
            )

        data_l = self.data
        data_r = other.data
        data = pd.concat([data_l, data_r])
        return ScalingModel(data, self.x, self.y, f"{self.x}_{self.y}" if name is None else name)

    def to_csv(self, filepath):
        """Export the constituent dataset this model is derived from to a CSV

        Args:
            filepath (str): the path to write the csv at.

        """
        self.data.to_csv(filepath, index=False)
