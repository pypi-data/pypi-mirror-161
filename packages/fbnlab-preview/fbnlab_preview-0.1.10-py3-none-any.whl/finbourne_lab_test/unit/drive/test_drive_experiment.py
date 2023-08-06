import os
import unittest
from pathlib import Path
from shutil import rmtree

from urllib3.response import HTTPResponse

from finbourne_lab import Convener
from finbourne_lab.drive import DriveExperiment
from finbourne_lab_test.utils.mock import make_request


def api_call(i) -> HTTPResponse:
    return make_request(i, 'drive')


class TestDriveExperiment(unittest.TestCase):

    work_dir = '/tmp/finbourne_lab_test/unit/drive/'

    @classmethod
    def setUpClass(cls) -> None:

        if os.path.exists(f'{cls.work_dir}'):
            rmtree(cls.work_dir)

        path = Path(cls.work_dir)
        path.mkdir(parents=True, exist_ok=True)

    def test_experiment_run(self):

        def build(x):
            return lambda: api_call(x)

        ex = DriveExperiment(build, [1, 1000])
        c = Convener(ex, self.work_dir, 'run_1')
        c.go(10)

        df = c.read_csv()

        self.assertEqual(10, df.shape[0])
        self.assertEqual(0, df[df.client_time.isna()].shape[0])
        self.assertEqual(0, df[df.server_time.isna()].shape[0])
