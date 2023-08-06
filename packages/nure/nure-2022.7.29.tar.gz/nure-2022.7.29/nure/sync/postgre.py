import json

import sqlalchemy
import nure.sync.sql


class PostgreSql(nure.sync.sql.Sql):
    def __init__(self, secret_fn, suffix_func, root_path='data/postgre', ttl=None) -> None:
        super(PostgreSql, self).__init__(suffix_func, root_path, ttl)
        with open(secret_fn, 'rt') as fd:
            secret = json.load(fd)

        user = secret['user']
        password = secret['password']
        host = secret['host']
        port = secret['port']
        dbname = secret['dbname']

        self._engine = sqlalchemy.create_engine(
            f'postgresql://{user}:{password}@{host}:{port}/{dbname}')

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        return self._engine
