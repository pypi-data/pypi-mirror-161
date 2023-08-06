import os
import unittest
from pathlib import Path
from finbourne_lab_test.utils.test_experiment import TestExperiment
from finbourne_lab import Convener
import time
from shutil import rmtree
import numpy as np
import pandas as pd


class TestBaseExperimentAndConvener(unittest.TestCase):

    """Test the basic mechanics of the BaseExperiment class and how the Convener class uses it.

    """

    work_dir = '/tmp/finbourne_lab_test/base_exp_and_convener/'

    @classmethod
    def setUpClass(cls) -> None:

        if os.path.exists(f'{cls.work_dir}'):
            rmtree(cls.work_dir)

        path = Path(cls.work_dir)
        path.mkdir(parents=True, exist_ok=True)

        def build(x, y):
            if np.random.uniform() > y:
                raise ValueError("TEST ERROR")
            return lambda: time.sleep(x / 1000)

        cls.ex = TestExperiment(build, [1, 1000], 999.0)
        cls.err_ex = TestExperiment(build, [1, 1000], 0.5)

    def test_convener_and_experiment_construction(self):

        self.assertEqual(self.ex._ranges, ([1, 1000], 999.0))

        c = Convener(self.ex, self.work_dir, 'convener_build', seed=1994)

        # work dir and name are set and can be retrieved
        self.assertEqual(c.get_name(), 'convener_build')
        self.assertEqual(c.get_work_dir(), self.work_dir)

        # data path is correct
        self.assertEqual(c.data_file_path, f'{self.work_dir}/data/convener_build.csv')

        # experiment can be retrieved
        self.assertEqual(hash(self.ex), hash(c.get_experiment()))

        # Seed is set properly
        self.assertEqual(c._Convener__seed, 1994)

        # n parallel defaults to 1
        self.assertEqual(c._Convener__n_parallel, 1)

        # error wait defaults to 1
        self.assertEqual(c._Convener__err_wait, 1)

        # Sets up the working directory properly
        data_dir = c.data_file_path.replace('convener_build.csv', '')
        self.assertTrue(os.path.exists(data_dir))
        self.assertTrue(os.path.exists(data_dir.replace('/data/', '/plots/')))

        cc = Convener(self.ex, self.work_dir, 'convener_build', seed=1994, n_parallel=10, err_wait=15, soak_time=10)

        # n parallel can be set
        self.assertEqual(cc._Convener__n_parallel, 10)

        # error wait can be set
        self.assertEqual(cc._Convener__err_wait, 15)

        # error wait can be set
        self.assertEqual(cc._Convener__soak_time, 10)

    def test_sequential_base_experiment(self):

        c = Convener(self.ex, self.work_dir, 'base_sequential', seed=1989)
        c.go(5)
        df = c.read_csv()

        self.assertEqual(df.shape[0], 5)
        self.assertSequenceEqual(df.arg0.tolist(), [235, 117, 321, 824, 418])
        self.assertEqual(df[df.errored].shape[0], 0)

        self.assertEqual(c._Convener__seed, 1989 + 5)

        self.assertTrue('arg0' in df.columns and 'arg1' in df.columns)
        self.assertTrue((df.arg1 == 999.0).all())
        self.assertTrue(((df.arg0 >= 1) & (df.arg0 <= 1000)).all())

    def test_concurrent_base_experiment(self):

        np.random.seed(100)
        c = Convener(self.ex, self.work_dir, 'base_concurrent', n_parallel=5, seed=1989, soak_time=1)
        c.go(5)
        df = c.read_csv()
        df['start'] = pd.to_datetime(df.start)

        self.assertEqual(df[df.errored].shape[0], 0)
        self.assertEqual(df.experiment_id.unique().shape[0], 5)
        gdf = df.groupby('experiment_id').agg(
            arg0=('arg0', 'first'),
            start=('start', 'min'),
            n_parallel_exp=('n_parallel', 'first'),
        ).sort_values('start')
        self.assertSequenceEqual(gdf.arg0.tolist(), [203, 170, 909, 140, 385])
        self.assertTrue((df.arg1 == 999.0).all())
        self.assertTrue(((df.arg0 >= 1) & (df.arg0 <= 1000)).all())

    def test_sequential_base_experiment_error_capture(self):

        c = Convener(self.err_ex, self.work_dir, 'base_sequential_errors', seed=1989)
        c.go(5)
        df = c.read_csv()

        self.assertEqual(df.shape[0], 5)
        err_df = df[df.errored]
        self.assertEqual(err_df.shape[0], 1)
        self.assertTrue(['TEST ERROR' in em for em in err_df.error_message])
        self.assertTrue((df.arg1 == 0.5).all())
        self.assertTrue(((df.arg0 >= 1) & (df.arg0 <= 1000)).all())

    def test_concurrent_base_experiment_error_capture(self):

        c = Convener(self.err_ex, self.work_dir, 'base_concurrent_errors', n_parallel=5, seed=1992, soak_time=1)
        c.go(5)
        df = c.read_csv()

        self.assertEqual(df.experiment_id.unique().shape[0], 5)
        err_df = df[df.errored]
        self.assertGreater(err_df.shape[0], 0)
        self.assertTrue(['TEST ERROR' in em for em in err_df.error_message])
        self.assertTrue((df.arg1 == 0.5).all())
        self.assertTrue(((df.arg0 >= 1) & (df.arg0 <= 1000)).all())

    def test_randomised_concurrency_base_experiment(self):

        c = Convener(self.ex, self.work_dir, 'base_random_concurrent', n_parallel=[1, 5], seed=1992, soak_time=1)
        c.go(5)
        df = c.read_csv()
        df['start'] = pd.to_datetime(df.start)

        self.assertEqual(df.experiment_id.unique().shape[0], 5)
        self.assertEqual(df[df.errored].shape[0], 0)
        gdf = df.groupby('experiment_id').agg(
            arg0=('arg0', 'first'),
            start=('start', 'min'),
            n_parallel_exp=('n_parallel', 'first'),
            n_parallel_obs=('arg0', 'count'),
        ).sort_values('start')
        self.assertSequenceEqual(gdf.arg0.tolist(), [677, 293, 44, 122, 685])
        self.assertTrue(((df.n_parallel >= 1) & (df.n_parallel <= 5)).all())
