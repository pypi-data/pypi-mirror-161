from .experiment import LuminesceExperiment
from .measurements import LuminesceMeasurementFactory
from ..common.convener import Convener
from finbourne_lab.lusid.client import LusidClient
import uuid
from math import ceil
from typing import Tuple


class LusidWriters(LuminesceMeasurementFactory):
    """A factory class with methods that build conveners for different lusid write provider performance measurements.

    """

    def __init__(self, atlas, client_code, work_dir):
        """Constructor of the LusidWriters class

        Args:
            atlas (Atlas): a lumipy atlas to use in the experiments.
            client_code (str): the client code to send requests to. Must be the same as the one the atlas points to.
            work_dir (str): the working directory to create folders and write results in

        """

        self.lusid = LusidClient(
            token=atlas.get_client().get_token(),
            api_url=f'https://{client_code}.lusid.com/api',
        )
        self.scope = 'fbnlab-luminesce-lusid-writers'
        self.pf_scopes = []
        super().__init__(atlas, work_dir)

    def setup(self):
        self._ensure_instruments()

    def _clear_scopes(self, measurement):
        prefix = f'{self.scope}-{measurement}'
        print(f"Cleaning up test scopes ({prefix}*)")

        pf = self.atlas.lusid_portfolio()
        pf_scopes = pf.select_distinct(
            pf.portfolio_scope
        ).where(
            pf.portfolio_scope.str.startswith(prefix)
        ).go(quiet=True).PortfolioScope

        for pf_scope in pf_scopes:
            print('Deleting ' + pf_scope)
            self.lusid.delete_scope(pf_scope)

    def teardown(self):
        self._clear_scopes('transactions')
        self._clear_scopes('holdings')
        self._clear_scopes('instruments')
        self._clear_scopes('portfolios')

    def lusid_instrument_write(self, n_inst, n_para=1, soak_time=None) -> Tuple[Convener, Convener]:
        """Create a lusid instruments writer convener pair. One for the whole write query and another for the test
        data acquisition step alone (the baseline).

        Args:
            n_inst (Union[int, Tuple[int]]): single value or interval to sample over for number of instruments.
            n_para (Union[int, Tuple[int]]): single value or interval to sample over for number of parallel experiments to run
            soak_time (int): time to run repeated observations for when running parallel experiments.

        Notes:
            File naming convention: instruments_write_i[range or value]_NP[range or value] where i labels the instrument
            number range/value and NP labels the number of parallel experiments.

        Returns:
            Tuple[Convener, Convener]: a convener pair where the first is the write measurement and the second is the baseline
        """

        insts_to_write = self.atlas.lab_testdata_lusid_instrument().select('*')

        def build(x):
            tv = insts_to_write.limit(x).to_table_var()
            inst_writer = self.atlas.lusid_instrument_writer(to_write=tv)
            return inst_writer.select('*')

        def baseline(x):
            tv = insts_to_write.limit(x).to_table_var()
            return tv.select('*').limit(1)

        i_label = self.make_range_label(n_inst, 'i')
        np_label = self.make_range_label(n_para, 'NP')

        ex = LuminesceExperiment(build, n_inst)
        ex_base = LuminesceExperiment(baseline, n_inst)
        name = f'instruments_write_{i_label}_{np_label}'

        return (
            Convener(ex, self.work_dir, name, n_parallel=n_para, soak_time=soak_time),
            Convener(ex_base, self.work_dir, name + '_baseline', n_parallel=n_para, soak_time=soak_time),
        )

    def lusid_portfolio_write(self, n_pf, n_para=1, soak_time=None) -> Tuple[Convener, Convener]:
        """Create a lusid portfolio writer convener pair. One for the whole write query and another for the test
        data acquisition step alone (the baseline).


        Args:
            n_pf (Union[int, Tuple[int]]): single value or interval to sample over for number of portfolios.
            n_para (Union[int, Tuple[int]]): single value or interval to sample over for number of parallel experiments to run
            soak_time (int): time to run repeated observations for when running parallel experiments.

        Notes:
            File naming convention: portfolios_write_pf[range or value]_NP[range or value] where pf labels the portfolio
            number range/value and NP labels the number of parallel experiments.

        Returns:
            Tuple[Convener, Convener]: a convener pair where the first is the write measurement and the second is the baseline

        """

        scope = self.scope + '-portfolios'

        def build(x, y):
            _scope = y + '-' + str(uuid.uuid4()).split('-')[0]
            pd_data = self.atlas.lab_testdata_lusid_portfolio(scope=_scope).select('*').limit(x).to_table_var()
            return self.atlas.lusid_portfolio_writer(to_write=pd_data).select('*')

        def baseline(x, y):
            _scope = y + '-' + str(uuid.uuid4()).split('-')[0]
            pd_data = self.atlas.lab_testdata_lusid_portfolio(scope=_scope).select('*').limit(x).to_table_var()
            return pd_data.select('*').limit(1)

        pf_label = self.make_range_label(n_pf, 'pf')
        np_label = self.make_range_label(n_para, 'NP')

        ex = LuminesceExperiment(build, n_pf, scope)
        ex_base = LuminesceExperiment(baseline, n_pf, scope)
        name = f'portfolios_write_{pf_label}_{np_label}'

        return (
            Convener(ex, self.work_dir, name, n_parallel=n_para, soak_time=soak_time),
            Convener(ex_base, self.work_dir, name + '_baseline', n_parallel=n_para, soak_time=soak_time),
        )

    def lusid_portfolio_holding_write(self, n_hld, insts_per_pf, eff_ats_per_inst, n_para=1, soak_time=None) -> Tuple[Convener, Convener]:
        """Create a lusid holdings writer convener pair for a given data shape. One for the whole write query and another for the test
        data acquisition step alone (the baseline).
        The holdings write can depend on the number of portfolios being written to as well as the number of effecyive ats for a given block of of holdings.
        This will create a new scope and set of portfolios each time before doing the holdings write.


        Args:
            n_hld (Union[int, Tuple[int]]): single value or interval to sample over for number of holdings.
            insts_per_pf (Union[int, Tuple[int]]): single value or interval to sample over for number of instruments per portfolio in the holdings set.
            eff_ats_per_inst (Union[int, Tuple[int]]): single value or interval to sample over for number of effective at dates per instrument in the holdings set.
            n_para (Union[int, Tuple[int]]): single value or interval to sample over for number of parallel experiments to run
            soak_time (int): time to run repeated observations for when running parallel experiments.

        Notes:
            File naming convention: holdings_write_h[range or value]_ipp[range or value]_eapi[range or value]_NP[range or value] where
            h labels the holdings number value or range, ipp is the instruments per portfolio value or range, eapi is the effective
            ats per instrument value or range and NP is the parallelism value or range.

        Returns:
            Tuple[Convener, Convener]: a convener pair where the first is the write measurement and the second is the baseline

        """

        def build(x, y, z, scope_prefix):
            _n_pf = ceil(x/(y*z))

            _scope = scope_prefix + '-' + str(uuid.uuid4()).split('-')[0]
            self._ensure_portfolios(_n_pf, _scope, False)
            tv = self.atlas.lab_testdata_lusid_holding(
                scope=_scope,
                num_portfolios=_n_pf,
                instruments_per_portfolio=y,
                effective_ats_per_instrument=z,
                luids=self.luids
            ).select('*').limit(x).to_table_var()
            writer = self.atlas.lusid_portfolio_holding_writer(to_write=tv)
            return writer.select('*')

        def baseline(x, y, z, scope_prefix):
            _n_pf = ceil(x/(y*z))

            _scope = scope_prefix + '-' + str(uuid.uuid4()).split('-')[0]
            tv = self.atlas.lab_testdata_lusid_holding(
                scope=_scope,
                num_portfolios=_n_pf,
                instruments_per_portfolio=y,
                effective_ats_per_instrument=z,
                luids=self.luids
            ).select('*').limit(x).to_table_var()
            return tv.select('*').limit(1)

        h_label = self.make_range_label(n_hld, 'h')
        ipp_label = self.make_range_label(insts_per_pf, 'ipp')
        eapi_label = self.make_range_label(eff_ats_per_inst, 'eapi')

        shape_str = f'{h_label}_{ipp_label}_{eapi_label}'
        scope = self.scope + '-holdings-' + shape_str

        ex = LuminesceExperiment(build, n_hld, insts_per_pf, eff_ats_per_inst, scope)
        ex_base = LuminesceExperiment(baseline, n_hld, insts_per_pf, eff_ats_per_inst, scope)
        np_label = self.make_range_label(n_para, 'NP')
        name = f'holdings_write_{shape_str}-{np_label}'

        return (
            Convener(ex, self.work_dir, name, soak_time=soak_time),
            Convener(ex_base, self.work_dir, name + '_baseline', soak_time=soak_time),
        )

    def lusid_portfolio_transaction_write(self, n_txns, insts_per_pf, txns_per_inst, n_para=1, soak_time=None) -> Tuple[Convener, Convener]:
        """Create a lusid transactions writer convener pair for a given data shape. One for the whole write query and another for the test
        data acquisition step alone (the baseline).
        The transactions write can depend on the number of portfolios being written to as well as the number of transactions.
        This will create a new scope and set of portfolios each time before doing the transactions write.


        Args:
            n_txns (Union[int, Tuple[int]]): single value or interval to sample over for number of holdings.
            insts_per_pf (Union[int, Tuple[int]]): single value or interval to sample over for number of instruments per portfolio in the holdings set.
            txns_per_inst (Union[int, Tuple[int]]): single value or interval to sample over for number of effective at dates per instrument in the holdings set.
            n_para (Union[int, Tuple[int]]): single value or interval to sample over for number of parallel experiments to run
            soak_time (int): time to run repeated observations for when running parallel experiments.

        Notes:
            File naming convention: transactions_write_t[range or value]_ipp[range or value]_tpi[range or value]_NP[range or value] where
            h labels the transactions number value or range, ipp is the instruments per portfolio value or range, tpi is the number of transactions
            per instrument value or range and NP is the parallelism value or range.

        Returns:
            Tuple[Convener, Convener]: a convener pair where the first is the write measurement and the second is the baseline

        """

        def build(x, y, z, scope_prefix):
            _n_pf = ceil(x/(y*z))

            _scope = scope_prefix + '-' + str(uuid.uuid4()).split('-')[0]
            self._ensure_portfolios(_n_pf, _scope, False)
            tv = self.atlas.lab_testdata_lusid_transaction(
                scope=_scope,
                num_portfolios=_n_pf,
                instruments_per_portfolio=y,
                txns_per_instrument=z,
                luids=self.luids
            ).select('*').limit(x).to_table_var()
            writer = self.atlas.lusid_portfolio_txn_writer(to_write=tv)
            return writer.select('*')

        def baseline(x, y, z, scope_prefix):
            _n_pf = ceil(x/(y*z))
            tv = self.atlas.lab_testdata_lusid_transaction(
                scope='dummy-scope',
                num_portfolios=_n_pf,
                instruments_per_portfolio=y,
                txns_per_instrument=z,
                luids=self.luids
            ).select('*').limit(x).to_table_var()
            return tv.select('*').limit(1)

        t_label = self.make_range_label(n_txns, 't')
        ipp_label = self.make_range_label(insts_per_pf, 'ipp')
        tpi_label = self.make_range_label(txns_per_inst, 'tpi')

        shape_str = f'{t_label}_{ipp_label}_{tpi_label}'
        scope = self.scope + '-transactions-' + shape_str

        ex = LuminesceExperiment(build, n_txns, insts_per_pf, txns_per_inst, scope)
        ex_base = LuminesceExperiment(baseline, n_txns, insts_per_pf, txns_per_inst, scope)
        np_label = self.make_range_label(n_para, 'NP')
        name = f'transactions_write_{shape_str}-{np_label}'

        return (
            Convener(ex, self.work_dir, name, soak_time=soak_time),
            Convener(ex_base, self.work_dir, name + '_baseline', soak_time=soak_time),
        )
