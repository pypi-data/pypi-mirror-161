import pandas as pd


class Postprocessing:
    """This class enriches an existing luminesce measurement dataset by adding the server-side data.

    """

    def __init__(self, atlas):
        """Constructor of the dataset enricher.

        Args:
            atlas (Atlas): lumipy atlas to use to get the server side data.

        """
        self.atlas = atlas

    def __call__(self, c):

        ex_df = c.read_csv()
        ex_df['start'] = pd.to_datetime(ex_df.start)
        ex_df['end'] = pd.to_datetime(ex_df.end)

        start = ex_df.start.min().to_pydatetime()
        end = ex_df.end.max().to_pydatetime()
        hcq = self.atlas.sys_logs_hcquery(start_at=start, end_at=end)

        cols = [hcq.execution_id, hcq.data_volume,
                hcq.total_time_ms, hcq.fill_table_time_ms,
                hcq.merge_sql_time_ms, hcq.provider_time_ms,
                hcq.prep_time_ms]
        tv = hcq.select(*cols).to_table_var()
        qry = tv.select('*').where(tv.execution_id.is_in(ex_df.execution_id.tolist()))
        _df = qry.go()
        _df.iloc[:, 2:] = _df.iloc[:, 2:] / 1000

        m_df = pd.merge(ex_df, _df, left_on='execution_id', right_on='ExecutionId')
        m_df = m_df[[c for c in m_df.columns if c != 'ExecutionId']]
        m_df.to_csv(c.data_file_path.replace('.csv', '_enriched.csv'), index=False)
        return m_df
