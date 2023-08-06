import csv
import os
import re
from abc import abstractmethod

import sqlalchemy
import nure.sync.cache


class Sql(nure.sync.cache.LocalFileCache):
    def __init__(self, suffix_func, root_path='data/sql', ttl=None) -> None:
        super(Sql, self).__init__(root_path, ttl)
        self.suffix_func = suffix_func

    @property
    @abstractmethod
    def engine(self) -> sqlalchemy.engine.Engine:
        raise NotImplementedError()

    def key_to_local_relative_path(self, key, *args, **kargs) -> str:
        fn, _ = os.path.splitext(os.path.basename(key))
        suffix = self.suffix_func(*args, **kargs)
        return f'{fn}{suffix}.csv'

    def retrieve(self, sql_key, local_file_path,
                 re_replace=None, sa_replace=None, partition_size=10000):
        with open(sql_key, 'rt') as fd:
            sql_str = fd.read()

        if isinstance(re_replace, dict):
            for pattern, repl in re_replace.items():
                sql_str = re.sub(pattern, repl, sql_str)

        with self.engine.connect().execution_options(stream_results=True) as conn:
            conn: sqlalchemy.engine.Connection
            result: sqlalchemy.engine.ResultProxy = conn.execute(sqlalchemy.text(sql_str), sa_replace or {})

            with open(local_file_path, 'wt', newline='') as csv_file:
                writer = csv.writer(csv_file, dialect='excel')
                writer.writerow(result.keys())

                while len(rows := result.fetchmany(size=partition_size)) > 0:
                    writer.writerows(rows)
