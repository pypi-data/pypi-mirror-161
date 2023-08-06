import sqlalchemy
import nure.sync.sql


class BigQuery(nure.sync.sql.Sql):
    def __init__(self, keyfile, suffix_func, arraysize=10_000, root_path='data/bigquery', ttl=None) -> None:
        super(BigQuery, self).__init__(suffix_func, root_path, ttl)

        self._engine = sqlalchemy.create_engine('bigquery://', credentials_path=keyfile, arraysize=arraysize)

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        return self._engine
