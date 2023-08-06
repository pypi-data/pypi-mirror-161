from __future__ import annotations

import datetime as dt

import pandas as pd
from urllib3 import HTTPResponse

from finbourne_lab.base import BaseExperiment
from finbourne_lab.base import BaseResult


class ApiResult(BaseResult):
    """Class that represents the result of a single observation of a Finbourne REST API call.

    """

    def __init__(self):
        self.call_start = pd.NaT
        self.call_end = pd.NaT
        self.client_time = None
        self.server_time = None
        self.failed = None
        super().__init__()


class ApiExperiment(BaseExperiment):
    """Class for experiments that measure calls to a Finbourne REST API such as the lusid or drive apis.

    """

    def __init__(self, build_fn, application, *ranges, **kwargs):
        """Constructor for the ApiExperiment class.

        Args:
            build_fn (Callable): a function that builds a callable given a set of values. This callable makes a request
            to the API in question and returns the HTTPResponse object.
            application (str): the name of the application the experiment is running against.
            *ranges: range pairs, single values or sets to sample when running experiments.

        Keyword Args:
            throw_on_failure (bool): whether to throw an error when the metadata header doesn't show a success.
            Sometimes a lusid call can fail but have a success status code.

        """

        self.application = application
        self.throw_on_failure = kwargs.get('throw_on_failure', True)

        super().__init__(build_fn, *ranges, **kwargs)

    def copy(self, seed: int):
        """Make a copy of the experiment so multiple copies of the experiment can be run in parallel.

        Args:
            seed (int): random seed to set in numpy when selecting experiment arg values.

        Returns:
            ApiExperiment: an independent copy of this experiment.
        """
        return type(self)(
            self.build_fn,
            *self._ranges,
            seed=seed,
            throw_on_failure=self.throw_on_failure,
        )

    def __str__(self):
        return f"{super().__str__()}  Throw on Fail: {self.throw_on_failure}"

    def _init_result(self) -> ApiResult:
        return ApiResult()

    def _job(self, runnable) -> None:

        self._return.call_start = dt.datetime.utcnow()
        response = runnable()
        self._return.call_end = dt.datetime.utcnow()
        self._return.client_time = (self._return.call_end - self._return.call_start).total_seconds()

        if not isinstance(response, HTTPResponse):
            self._force_stop = True
            raise TypeError(
                "Response object was not an HTTPResponse instance. "
                "You might need to set _preload_content=False in your sdk method call."
            )

        if response.status >= 400:
            raise ValueError(
                f"Received error response from {self.application}: "
                f"status code = {response.status}, reason = {response.reason}"
            )

        self._return.execution_id = response.getheader(f'{self.application}-meta-requestId')
        self._return.failed = not response.getheader(f'{self.application}-meta-success')
        self._return.server_time = int(response.getheader(f'{self.application}-meta-duration')) / 1000

        if self._return.failed and self.throw_on_failure:
            raise ValueError(
                f"The response from {self.application} contained failures ({self.application}-meta-success was false)"
            )
