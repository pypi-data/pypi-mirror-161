from importlib.util import find_spec
from math import ceil

from .experiment import LuminesceExperiment
from .measurements import LuminesceMeasurementFactory
from finbourne_lab.common.convener import Convener
from finbourne_lab.lusid.client import LusidClient

if find_spec('IPython') is not None:
    from IPython.display import clear_output


class LusidReaders(LuminesceMeasurementFactory):
    """A factory class with methods that build conveners for different lusid read provider performance measurements.

    """

    def __init__(self, atlas, client_code, work_dir):
        self.lusid = LusidClient(
            token=atlas.get_client().get_token(),
            api_url=f'https://{client_code}.lusid.com/api',
        )
        super().__init__(atlas, work_dir)

    def setup(self):
        self._ensure_instruments()

    def _ensure_transactions(self, n_pf, txns_per_pf, force):

        scope = self._ensure_portfolios(n_pf, f'fbnlab-txns-read_p{n_pf}_tpp{txns_per_pf}', force)

        # add the txns
        txns_data = self.atlas.lab_testdata_lusid_transaction(
            scope=scope,
            num_portfolios=n_pf,
            instruments_per_portfolio=txns_per_pf,
            txns_per_instrument=1,
            luids=self.luids,
        ).select('*').to_table_var()

        txn_write = self.atlas.lusid_portfolio_txn_writer(to_write=txns_data)
        tw_df = txn_write.select(
            txn_write.write_error_code, txn_write.write_error_detail
        ).where(
            txn_write.write_error_code != 0
        ).go()

        if (tw_df.WriteErrorCode != 0).any():
            err_msgs = '\n'.join(tw_df.WriteErrorDetail.iloc[:5])
            raise ValueError(
                f'The txns write contained {tw_df[tw_df.WriteErrorCode != 0].shape[0]} errors:\n{err_msgs}'
            )

        if find_spec('IPython') is not None:
            clear_output(wait=True)
            print(end='')

        return scope

    def _ensure_holdings(self, n_pf, hld_per_pf, force):

        scope = self._ensure_portfolios(n_pf, f'fbnlab-hldg-read_p{n_pf}_hpp{hld_per_pf}', force)

        # add the holdings
        hldg_data = self.atlas.lab_testdata_lusid_holding(
            scope=scope,
            num_portfolios=n_pf,
            instruments_per_portfolio=hld_per_pf,
            effective_ats_per_instrument=1,
            luids=self.luids,
        ).select('*').to_table_var()

        hld_write = self.atlas.lusid_portfolio_holding_writer(to_write=hldg_data)
        hw_df = hld_write.select(
            hld_write.write_error_code, hld_write.write_error_detail
        ).where(
            hld_write.write_error_code != 0
        ).go()
        if (hw_df.WriteErrorCode != 0).any():
            err_msgs = '\n'.join(hw_df.WriteErrorDetail.iloc[:5])
            raise ValueError(
                f'The holdings write contained {hw_df[hw_df.WriteErrorCode != 0].shape[0]} errors:\n{err_msgs}'
            )

        if find_spec('IPython') is not None:
            clear_output(wait=True)
            print(end='')

        return scope

    def lusid_portfolio_holding_read_measurement(self, n_hld, hld_per_pf, n_para=1, soak_time=None, force_setup=False) -> Convener:
        """Create a lusid portfolio holdings read convener over a test data scope. Can create the data if it's not already available or force overwrite.

        Args:
            n_hld (Union[int, Tuple[int]]): single value or interval to sample over for number of holdings.
            hld_per_pf (int): number of holdings per portfolio in the test scope
            n_para (Union[int, Tuple[int]]): single value or interval to sample over for number of parallel experiments to run
            soak_time (int): time to run repeated observations for when running parallel experiments.
            force_setup (Optional[False]): whether to force a rewrite when building the test scope data

        Notes:
            File naming convention: holdings_read_h[range or value]_hpp[range or value]_NP[range or value] where
            h is the holdings value or range, hpp is the holdings per portfolio value or range and NP is the parallelism value or range

        Returns:
            Convener: a convener that encapsulates the portfolio holding read measurement.

        """

        n_hld_max = n_hld if isinstance(n_hld, int) else max(n_hld)
        n_pf = ceil(n_hld_max / hld_per_pf)
        scope = self._ensure_holdings(n_pf, hld_per_pf, force=force_setup)

        hld = self.atlas.lusid_portfolio_holding()

        def build(x, y):
            return hld.select('*').where(hld.portfolio_scope == y).limit(x)

        h_label = self.make_range_label(n_hld, 'h')
        hpp_label = self.make_range_label(hld_per_pf, 'hpp')
        np_label = self.make_range_label(n_para, 'NP')

        ex = LuminesceExperiment(build, n_hld, scope)
        name = f'holdings_read_{h_label}_{hpp_label}_{np_label}'
        return Convener(ex, self.work_dir, name, n_parallel=n_para, soak_time=soak_time)

    def lusid_portfolio_transaction_read_measurement(self, n_txn, txns_per_pf, n_para=1, soak_time=None, force_setup=False) -> Convener:
        """Create a lusid portfolio transactions read convener over a test data scope. Can create the data if it's not already available or force overwrite.

        Args:
            n_txn (Union[int, Tuple[int]]): single value or interval to sample over for number of transactions.
            txns_per_pf (int): number of transactions per portfolio in the test scope
            n_para (Union[int, Tuple[int]]): single value or interval to sample over for number of parallel experiments to run
            soak_time (int): time to run repeated observations for when running parallel experiments.
            force_setup (Optional[False]): whether to force a rewrite when building the test scope data

        Notes:
            File naming convention: transactions_read_t[range or value]_tpp[range or value]_NP[range or value] where
            t is the n transactions value or range, tpp is the transactions per portfolio range or value and NP is the
            parallelism value or range.

        Returns:
            Convener: a convener that encapsulates the portfolio transaction read measurement.

        """

        n_txn_max = n_txn if isinstance(n_txn, int) else max(n_txn)
        n_pf = ceil(n_txn_max / txns_per_pf)
        scope = self._ensure_transactions(n_pf, txns_per_pf, force=force_setup)

        txn = self.atlas.lusid_portfolio_txn()

        def build(x, y):
            return txn.select('*').where(txn.portfolio_scope == y).limit(x)

        t_label = self.make_range_label(n_txn, 't')
        tpp_label = self.make_range_label(txns_per_pf, 'tpp')
        np_label = self.make_range_label(n_para, 'NP')

        ex = LuminesceExperiment(build, n_txn, scope)
        name = f'transactions_read_{t_label}_{tpp_label}_{np_label}'
        return Convener(ex, self.work_dir, name, n_parallel=n_para, soak_time=soak_time)

    def lusid_portfolio_read_measurement(self, n_pf, scope=None, n_para=1, soak_time=None) -> Convener:
        """Create a lusid portfolio read convener over an optional test data scope.

        Args:
            n_pf (Union[int, Tuple[int]]): single value or interval to sample over for number of portfolios.
            scope (Optional[str]): scope to read portfolio test data from. If not given the provider will not filter on scope.
            n_para (Union[int, Tuple[int]]): single value or interval to sample over for number of parallel experiments to run
            soak_time (int): time to run repeated observations for when running parallel experiments.

        Notes:
            File naming convention: portfolios_read_p[range or value]_NP[range or value] where
            p is the n portfolios value or range and NP is the parallelism value or range.

        Returns:
            Convener: a convener that encapsulates the portfolio read measurement.

        """

        pf = self.atlas.lusid_portfolio().select('*')

        def build(x, y):
            if y is None:
                return pf.limit(x)
            return pf.where(pf.portfolio_scope == y).limit(x)

        pf_label = self.make_range_label(n_pf, 'pf')
        np_label = self.make_range_label(n_para, 'NP')

        ex = LuminesceExperiment(build, n_pf, scope)
        name = f'portfolios_read_{pf_label}_{np_label}'
        if scope is not None:
            name += '_scoped'

        return Convener(ex, self.work_dir, name, n_parallel=n_para, soak_time=soak_time)

    def lusid_instrument_read_measurement(self, n_inst, scope=None, n_para=1, soak_time=None) -> Convener:
        """Create a lusid instruments read convener over an optional test data scope.

        Args:
            n_inst (Union[int, Tuple[int]]): single value or interval to sample over for number of instruments.
            scope (Optional[str]): scope to read instrument test data from. If not given the provider will not filter on scope.
            n_para (Union[int, Tuple[int]]): single value or interval to sample over for number of parallel experiments to run
            soak_time (int): time to run repeated observations for when running parallel experiments.

        Notes:
            File naming convention: instruments_read_i[range or value]_NP[range or value] where
            i is the n instruments value or range and NP is the parallelism value or range.

        Returns:
            Convener: a convener that encapsulates the instrument read measurement.

        """

        inst = self.atlas.lusid_instrument().select('*')

        def build(x, y):
            if y is None:
                return inst.limit(x)
            return inst.where(inst.scope == y)

        i_label = self.make_range_label(n_inst, 'i')
        np_label = self.make_range_label(n_para, 'NP')

        ex = LuminesceExperiment(build, n_inst, scope)
        name = f'instruments_read_{i_label}_{np_label}'
        if scope is not None:
            name += '_scoped'

        return Convener(ex, self.work_dir, name, n_parallel=n_para, soak_time=soak_time)
