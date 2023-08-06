import numpy as np
import pandas as pd
import datetime as dt
import uuid


def generate_data(x_min, x_max, n, c, m, s, outlier_prob=0.0) -> pd.DataFrame:

    """Helper function that generates linear relationship data for testing.

    Args:
        x_min (int): lower limit of the x range.
        x_max (int): upper limit of the x range.
        n (int): number of data points.
        c (float): the y intercept of the linear relationship
        m (float): the gradient of the linear relationship
        s (float): the standard deviation of the linear relationship's noise term.
        outlier_prob (Optional[float]): outlier probability. Defaults to 0.0 (no outliers)

    Returns:
        DataFrame: a dataframe containing the generated data.

    """

    x = np.random.randint(x_min, x_max, size=n)

    outliers = np.random.binomial(1, outlier_prob, size=x.shape) * s * 5
    y = x * m + np.random.uniform(c - s, c + s, size=x.shape) + outliers

    return pd.DataFrame(
        {
            'execution_id': [str(uuid.uuid4()) for _ in range(n)],
            'arg0': x,
            'errored': [False] * n,
            'force_stopped': [False] * n,
            'error_message': [None] * n,
            'call_time': y,
            'start': [dt.datetime.utcnow() + dt.timedelta(seconds=i) for i in range(n)]
        }
    )
