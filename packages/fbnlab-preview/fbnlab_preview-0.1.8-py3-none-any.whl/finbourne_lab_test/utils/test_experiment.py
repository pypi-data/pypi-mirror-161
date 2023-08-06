from __future__ import annotations
from finbourne_lab.base.experiment import BaseExperiment
from finbourne_lab.base.result import BaseResult


class TestExperiment(BaseExperiment):
    """

    """

    def copy(self, seed: int) -> TestExperiment:
        """Copy this experiment instance for parallel runs.

        Args:
            seed (int): random seed to use in the experiment

        Returns:
            TestExperiment: a copy of this experiment.
        """
        return TestExperiment(
            self.build_fn,
            *self._ranges,
            seed=seed
        )

    def _init_result(self) -> BaseResult:
        return super()._init_result()

    def _job(self, runnable) -> None:
        runnable()
