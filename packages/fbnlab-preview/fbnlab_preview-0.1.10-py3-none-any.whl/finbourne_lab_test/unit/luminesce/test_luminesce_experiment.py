import os
import unittest
from pathlib import Path
from shutil import rmtree

from finbourne_lab import Convener
from finbourne_lab.luminesce import LuminesceExperiment
from finbourne_lab_test.utils.mock import MockQuery


class TestLuminesceExperiment(unittest.TestCase):

    work_dir = '/tmp/finbourne_lab_test/unit/luminesce/'

    @classmethod
    def setUpClass(cls) -> None:

        if os.path.exists(f'{cls.work_dir}'):
            rmtree(cls.work_dir)

        path = Path(cls.work_dir)
        path.mkdir(parents=True, exist_ok=True)

    def test_mock_query_job(self):

        build = MockQuery.build

        qry = build(5)

        self.assertEqual(qry.x, 5)
        self.assertEqual(qry.call_count, 0)

        job = qry.go_async()
        job.interactive_monitor()

        df = job.get_result()
        self.assertSequenceEqual(df.shape, [5, 3])
        self.assertEqual(qry.call_count, 1)

    def test_sequential_experiment(self):

        n_experiments = 5

        build_fn = MockQuery.build
        experiment = LuminesceExperiment(build_fn, [1, 10])
        convener = Convener(experiment, self.work_dir, 'sequential', seed=1989)
        convener.go(n_experiments)

        df = convener.read_csv()

        self.assertEqual(df.shape[0], n_experiments)

        self.assertEqual(convener._Convener__seed, 1989 + n_experiments)
        self.assertEqual(experiment._ranges, ([1, 10],))

    def test_sequential_single_point_experiment(self):

        n_experiments = 5

        build_fn = MockQuery.build
        experiment = LuminesceExperiment(build_fn, 10)
        convener = Convener(experiment, self.work_dir, 'sequential_sp')
        convener.go(n_experiments)

        df = convener.read_csv()

        self.assertEqual(df.shape[0], n_experiments)
        self.assertTrue((df.arg0 == 10).all())

    def test_concurrent_experiment(self):

        n_experiments = 5
        n_parallel = 5

        build_fn = MockQuery.build
        experiment = LuminesceExperiment(build_fn, [1, 10])
        convener = Convener(experiment, self.work_dir, 'concurrent', seed=1989, n_parallel=n_parallel, soak_time=1)
        convener.go(n_experiments)

        df = convener.read_csv()

        self.assertEqual(df.shape[0], n_experiments * n_parallel)

        for ex_id, ex_df in df.groupby(df.experiment_id):
            self.assertEqual(ex_df.shape[0], n_parallel)
            param_vals = ex_df.arg0.tolist()
            self.assertTrue(all(0 < p <= 10 for p in param_vals))
            self.assertTrue(all(e == ex_id for e in ex_df.experiment_id))
            self.assertTrue(all(n == n_parallel for n in ex_df.n_parallel))

        self.assertEqual(convener._Convener__n_parallel, 5)
        self.assertEqual(convener._Convener__name, 'concurrent')
        self.assertEqual(convener._Convener__seed, 1989 + n_experiments)

        self.assertEqual(experiment._ranges, ([1, 10],))

        self.assertEqual(convener._Convener__work_dir, self.work_dir)
        self.assertFalse(df.errored.any())

    def test_random_concurrency(self):

        n_experiments = 5
        n_parallel = [1, 10]

        build_fn = MockQuery.build
        experiment = LuminesceExperiment(build_fn, [1, 10])
        convener = Convener(experiment, self.work_dir, 'concurrent_rand', n_parallel=n_parallel, soak_time=1)
        convener.go(n_experiments)

        df = convener.read_csv()
        gdf = df.groupby('experiment_id').agg(Count=('experiment_id', 'count'))

        self.assertGreater(gdf.Count.unique().shape[0], 1)
        self.assertTrue(all(1 <= c <= 10 for c in gdf.Count))

    def test_error_catch(self):

        n_experiments = 5

        build_fn = MockQuery.build
        experiment = LuminesceExperiment(build_fn, -1)
        convener = Convener(experiment, self.work_dir, 'error', err_wait=0)
        convener.go(n_experiments)

        df = convener.read_csv()

        self.assertEqual(df.shape[0], n_experiments)
        self.assertEqual(df[df.errored].shape[0], n_experiments)
        for error_message in df.error_message:
            self.assertIn("This is a test error", error_message)
