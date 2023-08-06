import datetime as dt
from typing import Union, List, Any, Set

import pandas as pd
from finbourne_lab.base.experiment import BaseExperiment
from finbourne_lab.base.result import BaseResult


class LuminesceResult(BaseResult):
    """Class that represents the result for a single luminesce query experiment.

    """

    def __init__(self):
        """Constructor for the luminesce experiment result class.

        """
        self.send = pd.NaT
        self.submitted = pd.NaT
        self.get = pd.NaT
        self.download_finish = pd.NaT
        self.obs_rows = None
        self.obs_cols = None
        self.start_query_time = None
        self.query_time = None
        self.download_time = None
        super().__init__()


class LuminesceExperiment(BaseExperiment):
    """Class that encapsulates a luminesce experiment.

    """

    def __init__(
            self,
            build_fn,
            *ranges: Union[List[Union[int, float]], Any, Set[Any]],
            **kwargs: Any
    ):
        """Constructor for the experiment class.

        Args:
            build_fn (Callable): a function that returns a lumipy query object when given a set of values.
            *ranges (Union[List[Union[int, float]], Union[int, float]]): single constant values or ranges to randomly
            sample for the experiment.

        Keyword Args:
            seed (int): random seed to set in numpy when selecting experiment arg values.
            skip_download (Optional[bool]): whether to skip downloading the query (defaults to True).

        """
        self.skip_download = kwargs.get('skip_download', True)
        self.check_period = kwargs.get('check_period', 0.1)
        self.keep_for = kwargs.get('keep_for', 900)
        super().__init__(build_fn, *ranges, **kwargs)

    def __str__(self):
        return f"{super().__str__()}  " \
               f"Skip Download: {self.skip_download}  " \
               f"Check Period: {self.check_period}  " \
               f"Keep for {self.keep_for}"

    def copy(self, seed: int):
        """Make an independent copy of this experiment object.

        Args:
            seed (int): random seed to set in numpy when selecting experiment arg values.

        Returns:
            LuminesceExperiment: an independent copy of this experiment.
        """
        return LuminesceExperiment(self.build_fn, *self._ranges, seed=seed, skip_download=self.skip_download, keep_for=self.keep_for)

    def _init_result(self) -> LuminesceResult:
        return LuminesceResult()

    def _job(self, runnable) -> None:

        qry = runnable

        if self.should_stop():
            return

        self._return.send = dt.datetime.utcnow()
        job = qry.go_async(keep_for=self.keep_for)
        self._return.execution_id = job.ex_id
        self._return.submitted = dt.datetime.utcnow()
        self._return.start_query_time = (self._return.submitted - self._return.send).total_seconds()

        if self.should_stop():
            return

        job.interactive_monitor(True, self.check_period, self.should_stop)
        if job._status == 'Faulted':
            message_lines = [l for l in job._progress_lines if l.strip() != '']
            message = '\n'.join(message_lines[-10:])
            raise ValueError(f'Query {job.ex_id} has ended in an error state:\n\n{message}')

        self._return.get = dt.datetime.utcnow()
        self._return.query_time = (self._return.get - self._return.submitted).total_seconds()

        if self.should_stop() or self.skip_download:
            return

        df = job.get_result(False)
        self._return.download_finish = dt.datetime.utcnow()

        self._return.obs_rows = df.shape[0]
        self._return.obs_cols = df.shape[1]

        self._return.download_time = (self._return.download_finish - self._return.get).total_seconds()
