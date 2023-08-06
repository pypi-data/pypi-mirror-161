import datetime as dt
import os
import time
import uuid
from pathlib import Path
from tqdm import tqdm

import numpy as np
import pandas as pd

from finbourne_lab.base.experiment import BaseExperiment
from multiprocessing import Queue


class Convener:
    """The convener class looks after the running of experiments and recording their data.

    """

    def __init__(
            self,
            experiment: BaseExperiment,
            work_dir: str,
            name: str,
            seed=None,
            err_wait=1,
            n_parallel=1,
            soak_time=None,
    ):
        """Constructor of the convener class.

        Args:
            experiment (BaseExperiment): the experiment to run.
            work_dir (str): the working directory to write results to.
            name (str): the name of the experiment.
            seed (Optional[int]): random seed to set at the start of the experimental run. Will be chosen randomly if
            not specified.
            err_wait (Optional[int]): number of seconds to wait after getting an error.
            n_parallel (Optional[Union[int, List[int]]]): number of concurrent runs of the experiment to run each time.
            soak_time (Optional[int]): time in seconds to run repeated experiment iterations for.

        """

        self.__validate_concurrency(n_parallel, soak_time)

        self.__work_dir = work_dir
        self.__name = name
        self.__experiment = experiment
        self.__seed = seed if seed is not None else np.random.randint(1989)
        self.__err_wait = err_wait
        self.__n_parallel = n_parallel
        self.__soak_time = soak_time
        self.__force_stop = False

        data_dir = f'{self.__work_dir}/data'
        self.__data_file = f'{data_dir}/{self.__name}.csv'

        Path(data_dir).mkdir(parents=True, exist_ok=True)
        Path(f'{self.__work_dir}/plots').mkdir(parents=True, exist_ok=True)

    @staticmethod
    def __validate_concurrency(n_parallel, soak_time):

        if isinstance(n_parallel, int):
            _n_parallel = n_parallel
        elif isinstance(n_parallel, (list, tuple)) and len(n_parallel) == 2:
            _n_parallel = n_parallel[1]
        else:
            raise TypeError(
                'Input value to n_parallel must be either a single integer or a pair of integers as list/tuple. '
                f'Was {n_parallel} ({type(n_parallel).__name__}).'
            )

        if soak_time is None and _n_parallel > 1:
            raise ValueError(
                "When running concurrent experiments a value must be given for soak_time when building the convener."
            )

    def __job(self, n_obs) -> pd.DataFrame:

        np.random.seed(self.__seed + n_obs * 2)
        if isinstance(self.__n_parallel, int):
            n_parallel = self.__n_parallel
        elif isinstance(self.__n_parallel, (list, tuple)):
            n_parallel = np.random.randint(self.__n_parallel[0], self.__n_parallel[1] + 1)
        else:
            raise ValueError(f"Bad parallelism input: {self.__n_parallel}.")

        def set_seed():
            if self.__n_parallel == 1:
                return self.__seed
            else:
                return np.random.randint(0, 100000)

        seeds = [set_seed() for _ in range(n_parallel)]
        tasks = [self.__experiment.copy(s) for s in seeds]
        queues = [Queue() for _ in range(n_parallel)]

        try:
            for q, t in zip(queues, tasks):
                # noinspection PyProtectedMember
                t._attach_queue(q)._set_soak_time(self.__soak_time).start()

            [t.join(force=False) for t in tasks]

        except KeyboardInterrupt:
            tqdm.write("\n🛑 Quitting the experimental run...\n")
            [t.join(force=True) for t in tasks]
            self.__force_stop = True

        rows = []
        for q in queues:
            while not q.empty():
                row = q.get()
                row['n_parallel'] = n_parallel
                rows.append(row)

        if len(rows) == 0 and not self.__force_stop:
            raise ValueError(
                "Experiment processes produced no outputs. "
                "There may have been errors in the subprocesses that caused a crash."
            )

        return pd.DataFrame(rows)

    def go(self, n_obs) -> None:
        """Run the experiments.

        Args:
            n_obs (int): number of times to run the experiment and observe values.

        Notes:
            Can be halted with keyboard interrupt.

        """

        run_id = str(uuid.uuid4())

        # In case we want to restart a convener that was halted
        self.__force_stop = False

        error_count = 0
        run_start = dt.datetime.utcnow()
        offset = dt.datetime.now() - dt.datetime.utcnow()

        # Very important. Do not remove.
        emoji = np.random.choice(['🧪', '🔭', '⚗️', '🧬', '🔬', '📐'])

        times = []
        start = None
        total_obs = 0

        tqdm.write(f"Experiment: {self.__name}")
        tqdm.write(str(self.__experiment))
        tqdm.write(f"Output file: {self.__data_file}")
        tqdm.write(f"Run start: {(run_start + offset).strftime('%Y-%m-%d %H:%M:%S')}")

        if self.__n_parallel != 1:
            tqdm.write(f"Concurrency: {self.__n_parallel}  Soak Time: {self.__soak_time}")

        pbar = tqdm(
            range(1, n_obs + 1),
            desc=f'{emoji}Doing Science! ',
            unit='Obs',
            total=n_obs,
            bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
        )
        with pbar as t:

            for _ in t:

                new_start = dt.datetime.utcnow()
                if start is not None:
                    times.append((new_start - start).total_seconds())
                start = new_start

                if len(times) >= 1:
                    t_mean = np.mean(times)
                    est_len = n_obs * t_mean / 60
                    est_finish = run_start + dt.timedelta(minutes=est_len) + offset
                    postfix = {
                        'finish_at': f"{est_finish.strftime('%H:%M:%S')}",
                        'error_count': error_count,
                    }
                    if error_count > 0:
                        postfix['error_rate'] = f"{round(100 * error_count / total_obs, 2)}%"
                    t.set_postfix(**postfix)

                df = self.__job(n_obs)

                df['experiment_name'] = self.__name
                df['run_start'] = run_start
                experiment_id = str(uuid.uuid4())
                df['experiment_id'] = experiment_id

                if df.shape[0] > 0:
                    total_obs += df.iloc[0].n_parallel

                df['run_id'] = run_id
                df.to_csv(
                    self.__data_file,
                    index=False,
                    mode='a',
                    header=not os.path.exists(self.__data_file)
                )

                if self.__force_stop:
                    raise KeyboardInterrupt()

                errors = df[df.errored].error_message.tolist()
                if len(errors) > 0:
                    error_count += len(errors)
                    err_msg = '\n'.join(errors)
                    s = 's' if len(errors) > 1 else ''
                    tqdm.write(f"Error{s} in run {experiment_id}:\n{err_msg}")
                    time.sleep(self.__err_wait)

                self.__seed += 1

    @property
    def data_file_path(self) -> str:
        """Get the file path for the data CSV.

        Returns:
            str: the data csv file path
        """
        return self.__data_file

    def read_csv(self) -> pd.DataFrame:
        """Read the data CSV and return it as a pandas dataframe.

        Returns:
            DataFrame: the contents of the data CSV file.
        """
        return pd.read_csv(self.__data_file)

    def get_name(self) -> str:
        """Return the name of the experiment

        Returns:
            str: the name of the experiment
        """
        return self.__name

    def get_experiment(self) -> BaseExperiment:
        """Return the experiment object that this convener manages

        Returns:
            BaseExperiment: the experiment object
        """
        return self.__experiment

    def get_work_dir(self):
        """Return the path to the working directory that this convener writes to

        Returns:
            str: the working directory path
        """
        return self.__work_dir
