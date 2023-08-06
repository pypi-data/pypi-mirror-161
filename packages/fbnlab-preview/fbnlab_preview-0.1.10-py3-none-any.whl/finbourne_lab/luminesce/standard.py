import numpy as np

from finbourne_lab import Convener
from finbourne_lab.luminesce import LuminesceExperiment
from .measurements import LuminesceMeasurementFactory


class StandardMeasurementSet(LuminesceMeasurementFactory):

    def _reader_test(self, reader, n, x_rng, category, name, n_parallel_set, n_columns=None, check_period=0.1, keep=90):

        def build(x):
            p = reader()
            select = ['*'] if n_columns is None else p.get_columns()[:n_columns]
            return p.select(*select).limit(x)

        e = LuminesceExperiment(
            build,
            x_rng,
            skip_download=True,
            check_period=check_period,
            keep_for=keep
        )

        conveners = []
        for n_p in n_parallel_set:
            c = Convener(e, self.work_dir + f'/{category}', name + f'_NP{n_p}', n, n_parallel=n_p)
            conveners.append(c)

        return conveners

    def _file_read_test(self, reader, test_data_path, n, x_rng, name, n_parallel_set, check_period=0.1, keep=90):

        def fn(x):
            return reader(file=test_data_path, apply_limit=x).select('*')

        e = LuminesceExperiment(
            fn, x_rng,
            skip_download=True, check_period=check_period,
            keep_for=keep
        )

        conveners = []
        for n_p in n_parallel_set:
            c = Convener(e, self.work_dir + '/readers', f'{name}_NP{n_p}', n, n_parallel=n_p)
            conveners.append(c)

        return conveners

    def _join_test(self, reader, n, x_rng, m, name, n_parallel_set, check_period=0.1, keep=90):

        if isinstance(x_rng, int):
            x_rng = [1, x_rng]

        r = reader()

        test_data = r.select(*r.get_columns()[:m]).limit(x_rng[1]).to_table_var('test_data')

        tv = test_data.select('*').limit(x_rng[1]).to_table_var('x')

        def baseline_fn(x):
            return tv.select('*').limit(1)

        def build_fn(x):
            tv2 = tv.select('*').limit(x).to_table_var()
            a = tv2.with_alias('A')
            b = tv2.with_alias('B')
            join = a.left_join(b, on=b.i == a.i)
            return join.select('*')

        convener_pairs = []
        e = LuminesceExperiment(build_fn, x_rng, skip_download=True, check_period=check_period, keep_for=keep)
        e_base = LuminesceExperiment(baseline_fn, x_rng, skip_download=True, check_period=check_period, keep_for=keep)

        for n_p in n_parallel_set:
            work_dir = self.work_dir + '/core'
            c = Convener(e, work_dir, name + f'_NP{n_p}', n, n_parallel=n_p)
            c_base = Convener(e_base, work_dir, name + f'_NP{n_p}_baseline', n, n_parallel=n_p)
            convener_pairs.append((c_base, c))

        return convener_pairs

    def _writer_test(self, writer, test_data_path, n, x_rng, name, n_parallel_set, check_period=0.1, keep=90):

        if isinstance(x_rng, int):
            x_rng = [1, x_rng]

        csv = self.atlas.drive_csv(file=test_data_path, apply_limit=x_rng[1])
        name = writer.get_name() if name is None else name

        def baseline_fn(x):
            return csv.select('*').limit(1)

        def writer_fn(x):
            tv = csv.select('*').limit(x).to_table_var()
            return writer(to_write=tv).select('*')

        baseline_ex = LuminesceExperiment(
            baseline_fn, x_rng,
            skip_download=True, check_period=check_period,
            keep_for=keep
        )
        writer_ex = LuminesceExperiment(
            writer_fn, x_rng,
            skip_download=True, check_period=check_period,
            keep_for=keep
        )
        convener_pairs = []

        for n_p in n_parallel_set:
            baseline_cv = Convener(baseline_ex, self.work_dir + '/writers', f'{name}_baseline_NP{n_p}', n, n_parallel=n_p)
            writer_cv = Convener(writer_ex, self.work_dir + '/writers', f'{name}_NP{n_p}', n, n_parallel=n_p)
            convener_pairs.append((baseline_cv, writer_cv))

        return convener_pairs

    def _file_write_test(self, writer, file_type, n, x_rng, n_cols, name, n_parallel_set, check_period=0.1, keep=90):

        t = self.atlas.testing10m()
        name = writer.get_name() if name is None else name

        if isinstance(x_rng, int):
            x_rng = [1, x_rng]

        def baseline_fn(x):
            cols = np.random.choice(t.get_columns(), n_cols, replace=False)
            tv = t.select(*cols).limit(x_rng[1]).to_table_var()

            return tv.select('*').limit(1)

        def writer_fn(x):
            cols = np.random.choice(t.get_columns(), n_cols, replace=False)
            tv = t.select(*cols).limit(x_rng[1]).to_table_var()

            tv2 = tv.select('*').limit(x).to_table_var()
            return writer(
                tv2,
                type=file_type,
                path='/honeycomb/testing/',
                file_names=f'luminesceTest_{n_cols}Cols'
            ).select('*')

        baseline_ex = LuminesceExperiment(
            baseline_fn, x_rng,
            skip_download=True, check_period=check_period,
            keep_for=keep
        )
        writer_ex = LuminesceExperiment(
            writer_fn, x_rng,
            skip_download=True, check_period=check_period,
            keep_for=keep
        )
        convener_pairs = []

        for n_p in n_parallel_set:
            baseline_cv = Convener(baseline_ex, self.work_dir + '/writers', f'{name}_cols{n_cols}_baseline_NP{n_p}', n, n_parallel=n_p)
            writer_cv = Convener(writer_ex, self.work_dir + '/writers', f'{name}_cols{n_cols}_NP{n_p}', n, n_parallel=n_p)
            convener_pairs.append((baseline_cv, writer_cv))

        return convener_pairs

    def excel_read_measurement(self, **kwargs):
        """Create drive excel file read measurement conveners.

        Keyword Args:
            x_rng (Union[int, List[int]]): the x range of the measurement (number of rows to read). Can be a single
            integer or a pair of integers. Defaults to [1, 10000]
            xlsx_path (str): path in drive to the xlsx file to use in the measurement.
            n_parallel_set (Optional[List[int]]): a set of parallelism values to create conveners for.

        Returns:
            List[Convener]: list of conveners. One for each degree of parallelism.

        """

        x_rng = kwargs.get('x_rng', [1, 10000])
        path = kwargs.get('xlsx_path', "/honeycomb/testing/luminesceTest100k.xlsx")
        n_parallel_set = kwargs.get('n_parallel_set', (1,))
        keep = kwargs.get('keep_for', 90)

        reader = self.atlas.drive_excel
        return self._file_read_test(reader, path, n, x_rng, 'excel_read', n_parallel_set, keep=keep)

    def csv_read_measurement(self, **kwargs):
        """Create drive CSV file read measurement conveners.

        Keyword Args:
            x_rng (Union[int, List[int]]): the x range of the measurement (number of rows to read). Can be a single
            integer or a pair of integers. Defaults to [1, 10000]
            csv_path (str): path in drive to the csv file to use in the measurement.
            n_parallel_set (Optional[List[int]]): a set of parallelism values to create conveners for.

        Returns:
            List[Convener]: list of conveners. One for each degree of parallelism.

        """

        x_rng = kwargs.get('x_rng', [1, 10000])
        path = kwargs.get('csv_path', "/honeycomb/testing/luminesceTest100k.csv")
        n_parallel_set = kwargs.get('n_parallel_set', (1,))
        keep = kwargs.get('keep_for', 90)

        reader = self.atlas.drive_csv
        return self._file_read_test(reader, path, n, x_rng, 'csv_read', n_parallel_set, keep=keep)

    def excel_write_measurement(self, **kwargs):
        """Create drive excel write measurement conveners.

        Keyword Args:
            x_rng (Union[int, List[int]]): the x range of the measurement (number of rows to read). Can be a single
            integer or a pair of integers. Defaults to [1, 10000]
            n_cols (int): number of columns to write to the drive excel file
            n_parallel_set (Optional[List[int]]): a set of parallelism values to create conveners for.

        Returns:
            List[Tuple[Convener]]: list of convener pairs (first is the baseline measurement second is the main one)
            There is one pair for each degree of parallelism.

        """
        x_rng = kwargs.get('x_rng', [1, 10000])
        n_cols = kwargs.get('n_cols', 50)
        n_parallel_set = kwargs.get('n_parallel_set', (1,))
        keep = kwargs.get('keep_for', 90)

        writer = self.atlas.drive_saveas
        return self._file_write_test(writer, 'Excel', n, x_rng, n_cols, 'excel_write', n_parallel_set, keep=keep)

    def csv_write_measurement(self, **kwargs):
        """Create drive CSV write measurement conveners.

        Keyword Args:
            x_rng (Union[int, List[int]]): the x range of the measurement (number of rows to read). Can be a single
            integer or a pair of integers. Defaults to [1, 10000]
            n_columns (int): number of columns to write to the drive CSV file
            n_parallel_set (Optional[List[int]]): a set of parallelism values to create conveners for.

        Returns:
            List[Tuple[Convener]]: list of convener pairs (first is the baseline measurement second is the main one)
            There is one pair for each degree of parallelism.

        """
        x_rng = kwargs.get('x_rng', [1, 10000])
        n_cols = kwargs.get('n_cols', 50)
        n_parallel_set = kwargs.get('n_parallel_set', (1,))
        keep = kwargs.get('keep_for', 90)

        writer = self.atlas.drive_saveas
        return self._file_write_test(writer, 'Csv', n, x_rng, n_cols, 'csv_write', n_parallel_set, keep=keep)

    def view_measurement(self, **kwargs):
        """Create view read measurement conveners.

        The baseline measurement is how long it takes to query n-many rows with m-many columns from testing10m. The main
        measurement is how long it takes to do the same thing through a view.

        Keyword Args:
            x_rng (Union[int, List[int]]): the x range of the measurement (number of rows to read). Can be a single
            integer or a pair of integers. Defaults to [1, 10000]
            n_columns (int): number of columns to query for
            n_parallel_set (Optional[List[int]]): a set of parallelism values to create conveners for.

        Returns:
            List[Tuple[Convener]]: list of convener pairs (first is the baseline measurement second is the main one)
            There is one pair for each degree of parallelism.

        """
        x_rng = kwargs.get('x_rng', [1, 10000])
        n_columns = kwargs.get('n_columns', 5)
        n_parallel_set = kwargs.get('n_parallel_set', (1,))
        keep = kwargs.get('keep_for', 90)

        check_period = kwargs.get('check_period', 0.01 if n_columns < 10 else 0.1)

        t10m, t10m_view = self.atlas.testing10m, self.atlas.testing10mview
        baselines = self._reader_test(t10m, n, x_rng, 'core', f'select_{n_columns}', n_parallel_set, n_columns, check_period, keep=keep)
        view_tests = self._reader_test(t10m_view, n, x_rng, 'core', f'select_view_{n_columns}', n_parallel_set, n_columns, check_period, keep=keep)
        return list(zip(baselines, view_tests))

    def join_measurement(self, **kwargs):
        """Create join measurement conveners.

        The baseline measurement is how long it takes to read data into the table variable that will be joined to itself
        The main measurement is the read in + the join

        Keyword Args:
            x_rng (Union[int, List[int]]): the x range of the measurement (number of rows to read). Can be a single
            integer or a pair of integers. Defaults to [1, 10000]
            n_columns (int): number of columns on the table that will be joined.
            n_parallel_set (Optional[List[int]]): a set of parallelism values to create conveners for.

        Returns:
            List[Tuple[Convener]]: list of convener pairs (first is the baseline measurement second is the main one)
            There is one pair for each degree of parallelism.

        """
        x_rng = kwargs.get('x_rng', [1, 10000])
        n_columns = kwargs.get('n_columns', 5)
        n_parallel_set = kwargs.get('n_parallel_set', (1,))
        keep = kwargs.get('keep_for', 90)

        check_period = kwargs.get('check_period', 0.01 if n_columns < 10 else 0.1)
        t10m = self.atlas.testing10m
        return self._join_test(t10m, n, x_rng, n_columns, 'join' + f'_{n_columns}', n_parallel_set, check_period, keep=keep)