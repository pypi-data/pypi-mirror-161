import os
import unittest
from pathlib import Path
from shutil import rmtree
from time import sleep

import numpy as np

from finbourne_lab import Convener
from finbourne_lab.base.measurement_factory import BaseMeasurementFactory
from finbourne_lab_test.utils.test_experiment import TestExperiment


class UndocumentedMockMeasurementSet(BaseMeasurementFactory):

    def test1_undocumented_measurement(self, **kwargs):
        pass


class MockMeasurementSet(BaseMeasurementFactory):

    def __init__(self, work_dir):
        super().__init__(work_dir)

    def test1_paired_measurement(self, **kwargs):

        """Placeholder 1

        """

        x_max = kwargs.get('x_max', 1000)
        n_obs = kwargs.get('n_obs', 10)

        def build_a(x):
            return lambda: sleep(x*0.01 + 0.5)

        def build_b(x):
            return lambda: sleep(x*0.01 + 0.5 + np.random.normal(0.0, 0.1))

        ex_a = TestExperiment(build_a, [1, x_max])
        ex_b = TestExperiment(build_b, [1, x_max])

        c_a = Convener(ex_a, self.work_dir, 'test1_a', n_obs)
        c_b = Convener(ex_b, self.work_dir, 'test1_b', n_obs)

        return c_a, c_b

    def test2_single_measurement(self, **kwargs):

        """Placeholder 1

        """

        x_max = kwargs.get('x_max', 1000)
        n_obs = kwargs.get('n_obs', 10)

        def build(x):
            return lambda: sleep(x*0.01 + 0.5)

        ex = TestExperiment(build, [1, x_max])
        c = Convener(ex, self.work_dir, 'test2', n_obs)
        return c

    def test3_list_measurement(self, **kwargs):

        """Placeholder 1

        """

        x_max = kwargs.get('x_max', 1000)
        n_obs = kwargs.get('n_obs', 10)
        parallel_set = kwargs.get('parallel_set', (1, 5, 10))

        def build(x):
            return lambda: sleep(x*0.01 + 0.5)

        ex = TestExperiment(build, [1, x_max])
        conveners = []
        for n_p in parallel_set:
            c = Convener(ex, self.work_dir, f'test2_NP{n_p}', n_obs, n_parallel=n_p, soak_time=1)
            conveners.append(c)
        return conveners


class TestMeasurementSet(unittest.TestCase):

    work_dir = '/tmp/finbourne_lab_test/measurement_set/'

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(f'{cls.work_dir}'):
            rmtree(cls.work_dir)

        path = Path(cls.work_dir)
        path.mkdir(parents=True, exist_ok=True)

    def test_measurement_set_measurement_dict(self):

        ms = MockMeasurementSet(self.work_dir)

        mlist = ms.get_measurements()
        self.assertEqual(3, len(mlist))

        names = set(mlist.keys())
        expected_names = {'test1_paired_measurement', 'test2_single_measurement', 'test3_list_measurement'}
        self.assertEqual(names, expected_names)

    def test_measurement_set_convener_list(self):

        ms = MockMeasurementSet(self.work_dir)

        c_list = ms.list_conveners()
        self.assertEqual(6, len(c_list))

    def test_measurement_set_convener_list_with_input_kwargs(self):

        ms = MockMeasurementSet(self.work_dir)

        c_list = ms.list_conveners(n_obs=5, x_max=2000, parallel_set=(1, 50))
        self.assertEqual(5, len(c_list))
