from abc import ABC, abstractmethod
from concurrent.futures import (Executor, ProcessPoolExecutor,
                                ThreadPoolExecutor)
from datetime import datetime
from typing import Any, Union

import pandas as pd

from nure.debug import DEBUG
from nure.sync.s3 import S3, S3Uri


class VolatileObject(ABC):
    _default_pool_ = None

    def __init__(self, pool: Executor = None) -> None:
        super().__init__()
        if pool is None:
            if VolatileObject._default_pool_ is None:
                VolatileObject._default_pool_ = ThreadPoolExecutor() if DEBUG else ProcessPoolExecutor()
            pool = VolatileObject._default_pool_

        self.pool = pool
        self.future = None
        self.instance = None

    @abstractmethod
    def is_valid(self, *args: Any, **kwds: Any):
        raise NotImplementedError()

    @abstractmethod
    def retrieve(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError()

    def get_instance(self, *args: Any, force=False, **kwds: Any) -> Any:
        if self.future is None and (force or not self.is_valid(*args, **kwds)):
            self.future = self.pool.submit(self.retrieve, *args, **kwds)

        if self.future is not None and (force or self.future.done()):
            self.instance = self.future.result()
            self.future = None

        return self.instance


class TimeoutObject(VolatileObject):
    def __init__(self, ttl: float, pool: Executor = None) -> None:
        self.ttl = ttl
        self.mod_time = datetime.min
        super().__init__(pool)

    def is_valid(self):
        return (datetime.now() - self.mod_time).total_seconds() < self.ttl

    @abstractmethod
    def retrieve(self) -> Any:
        self.mod_time = datetime.now()
        return None


class S3Object(VolatileObject):
    def __init__(self, s3uri: Union[str, S3Uri],
                 s3: S3 = S3(), ttc: float = 60,
                 pool: Executor = None) -> None:
        self.s3uri = s3uri
        self.s3 = s3
        self.ttc = ttc
        self.last_check = datetime.min
        self.last_mod = datetime.min
        super().__init__(pool=pool)

    def get_last_mod(self) -> datetime:
        return self.s3.metadata(self.s3uri)['LastModified']

    def is_valid(self):
        # if not time to check
        if (datetime.now() - self.last_check).total_seconds() < self.ttc:
            return True

        last_mod = self.get_last_mod()
        self.last_check = datetime.now()
        return last_mod == self.last_mod

    def retrieve(self, ttl=1) -> Any:
        local_file = self.s3.require(self.s3uri, ttl=ttl)
        self.last_mod = self.get_last_mod()
        return local_file


class S3ParquetObject(S3Object):
    def retrieve(self, ttl=1) -> Any:
        local_file = super().retrieve(ttl=ttl)
        df = pd.read_parquet(local_file)
        return df
