from finbourne_lab.base.measurement_factory import BaseMeasurementFactory


class LuminesceMeasurementFactory(BaseMeasurementFactory):
    """The standard measurement set for Luminesce

    """

    def __init__(self, atlas, work_dir):
        """The constructor of the standard measurement set

        Args:
            atlas (Atlas): the lumipy atlas to use when running queries.
            work_dir (str): the working directory to use in the conveners of the standard measurement set.

        """
        self.atlas = atlas
        self.n = 10000
        self.luids = self._get_luids_query().to_table_var()
        super().__init__(work_dir)

    def _get_luids_query(self):
        inst = self.atlas.lusid_instrument()
        return inst.select(
            inst.lusid_instrument_id,
            inst.client_internal,
        ).where(
            inst.client_internal.str.startswith('lumi-test-instrument-')
        ).order_by(
            inst.client_internal.ascending()
        ).limit(self.n)

    def _ensure_instruments(self):

        # Check the test instruments are there
        qry = self._get_luids_query()
        inst_df = qry.go(quiet=True)
        if inst_df.shape[0] == self.n:
            print('All test instruments are present.')
            return

        # Otherwise upsert required test instruments
        print('Generating test instrument set...')
        tv = self.atlas.lab_testdata_lusid_instrument().limit(self.n).to_table_var()
        i_write = self.atlas.lusid_instrument_writer(to_write=tv)
        i_write.select(
            i_write.lusid_instrument_id
        ).order_by(
            i_write.client_internal.ascending()
        ).go(quiet=True)

    def _ensure_portfolios(self, n_pf, scope, force):

        # does the scope exist?
        pf = self.atlas.lusid_portfolio()
        qry = pf.select(pf.portfolio_scope).where(pf.portfolio_scope == scope).limit(1)
        scope_exists = qry.go(quiet=True).shape[0] == 1

        # no need to write anything
        if scope_exists and not force:
            return scope

        # make the portfolios
        pf_data = self.atlas.lab_testdata_lusid_portfolio(
            scope=scope
        ).select('*').limit(n_pf).to_table_var()

        pf_write = self.atlas.lusid_portfolio_writer(to_write=pf_data)
        pf_write.select(pf_write.portfolio_code).limit(1).go(quiet=True)

        return scope


