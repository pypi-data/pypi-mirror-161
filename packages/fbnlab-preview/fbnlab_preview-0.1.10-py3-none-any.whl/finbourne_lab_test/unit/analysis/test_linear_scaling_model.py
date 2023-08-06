import os
import unittest
from pathlib import Path
from shutil import rmtree

import numpy as np

from finbourne_lab import ScalingModel
from finbourne_lab_test.utils.test_data_generation import generate_data


class TestLinearScalingModel(unittest.TestCase):

    work_dir = '/tmp/finbourne_lab_test/linear_scaling_model/'

    @classmethod
    def setUpClass(cls) -> None:

        if os.path.exists(f'{cls.work_dir}'):
            rmtree(cls.work_dir)

        path = Path(cls.work_dir)
        path.mkdir(parents=True, exist_ok=True)

        n_rows = 1000
        np.random.seed(1989)

        cls.df1 = generate_data(1, 1000, n_rows, 1.0, 0.01, 0.1)
        cls.df2 = generate_data(1, 1000, n_rows, 0.5, 0.025, 0.1)
        cls.df3 = generate_data(1, 1000, n_rows, 0.5, 0.025, 3, 0.1)

    def test_scaling_model_fit_and_predict(self):

        mod_1 = ScalingModel(self.df1, 'arg0', 'call_time', 'model1')

        # Test the fit results meet expectations
        fit_df = mod_1.fit_results()
        quantiles = fit_df.index.tolist()
        c_pred = fit_df.c.round(2).tolist()
        m_pred = fit_df.m.round(2).tolist()

        self.assertSequenceEqual(quantiles, [0.05, 0.25, 0.5, 0.75, 0.95])
        self.assertSequenceEqual(c_pred, [0.91, 0.95, 1.0, 1.04, 1.09])
        self.assertSequenceEqual(m_pred, [0.01]*5)

        # Test that the prediction results meet expectations
        x_pred = [1, 10, 100, 1000, 10000, 100000]
        pred_df = mod_1.predict(x_pred).round(2)
        self.assertSequenceEqual(pred_df.index.tolist(), x_pred)

    def test_scaling_model_outlier_handling(self):

        mod_3 = ScalingModel(self.df3, 'arg0', 'call_time', 'model3')

        outliers = mod_3.outliers()
        mod_3_proc = mod_3.remove_outliers()

        self.assertEqual(outliers.shape[0], 102)
        self.assertEqual(outliers.shape[0] + mod_3_proc.data.shape[0], mod_3.data.shape[0])

    def test_scaling_model_outlier_operator_overloads(self):

        mod_1 = ScalingModel(self.df1, 'arg0', 'call_time', 'model1')
        mod_2 = ScalingModel(self.df2, 'arg0', 'call_time', 'model2')

        # subtraction
        mod_diff = mod_2 - mod_1
        fr_df_diff = mod_diff.fit_results()

        # addition
        mod_sum = mod_2 + mod_1
        fr_df_sum = mod_sum.fit_results()

        # division
        mod_ratio = mod_2 / mod_1
        fr_df_ratio = mod_ratio.fit_results()

        # multiplication
        mod_prod = mod_2 * mod_1
        fr_df_prod = mod_prod.fit_results()

        pass

    def test_scaling_model_merge(self):

        mod_1 = ScalingModel(self.df1, 'arg0', 'call_time', 'model1')
        mod_2 = ScalingModel(self.df2, 'arg0', 'call_time', 'model2')
        mod = mod_1.merge(mod_2)
        self.assertEqual(mod.data.shape[0], mod_1.data.shape[0] + mod_2.data.shape[0])

