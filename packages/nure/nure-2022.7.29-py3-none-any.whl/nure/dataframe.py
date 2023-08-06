import concurrent.futures
from typing import Callable, Dict, List, Union, Tuple

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.groupby import DataFrameGroupBy
from pandas.io.parsers import TextFileReader

from .array import _DEFAULT_N_WORKERS_, parallelize_iterable
from .code import LabelCoder
import more_itertools


def _apply_wrapper_(dataframe: DataFrame, apply_func, *args, **kwargs):
    return dataframe.apply(apply_func, *args, **kwargs)


def _groupby_apply_wrapper_(list_dataframe: Tuple[DataFrame], apply_func, *args, **kwargs):
    list_dataframe = list(list_dataframe)
    for i, dataframe in enumerate(list_dataframe):
        list_dataframe[i] = apply_func(dataframe, *args, **kwargs)

    concat_dataframe = None
    # concat results of different types
    if isinstance(list_dataframe[0], DataFrame):
        concat_dataframe = pd.concat(list_dataframe, copy=False)
    else:
        parameters = {
            'index': kwargs.get('index', None),
            'columns': kwargs.get('columns', None)
        }
        concat_dataframe = pd.DataFrame.from_records(list_dataframe, **parameters)

    return concat_dataframe


def apply(
        dataframe: DataFrame, func: Callable, *args,
        chunksize: int = None, executor: concurrent.futures.Executor = None,
        n_workers=_DEFAULT_N_WORKERS_, use_process=False,
        **kwargs):

    if chunksize is None:
        chunksize = max(len(dataframe) // n_workers, n_workers)

    def _generator_():
        for i in range(0, len(dataframe), chunksize):
            yield dataframe.iloc[i: i + chunksize]

    list_results = [result for result in parallelize_iterable(
        _generator_(), _apply_wrapper_, func, *args,
        executor=executor, n_workers=n_workers, use_process=use_process, **kwargs
    )]

    dataframe = pd.concat(list_results, copy=False)
    return dataframe


def groupby_apply(
        groups: DataFrameGroupBy, func: Callable, *args,
        chunksize: int = None, executor: concurrent.futures.Executor = None,
        n_workers=_DEFAULT_N_WORKERS_, use_process=False,
        **kwargs):

    # take only the dataframe
    groups = map(lambda g: g[1], groups)

    # chunkify the groups
    if chunksize is None:
        # divide return iterables
        # convert to list as the _groupby_apply_wrapper_ accept list
        # filter empty group which happens if n_groups < n_workers
        groups = more_itertools.divide(n_workers, groups)
        groups = map(list, groups)
        groups = filter(len, groups)
    else:
        groups = more_itertools.chunked(groups, chunksize)

    list_results = [result for result in parallelize_iterable(
        groups, _groupby_apply_wrapper_, func, *args,
        executor=executor, n_workers=n_workers, use_process=use_process, **kwargs
    )]

    dataframe = pd.concat(list_results, copy=False)

    return dataframe


def encode_dataframe(dataframe: DataFrame, columns: Union[List[str], Dict[str, LabelCoder]]):
    if not isinstance(columns, dict):
        columns = {cname: LabelCoder() for cname in columns}

    dataframe = dataframe.assign(**{
        cname: encoder.encode(dataframe[cname].values) for cname, encoder in columns.items()
    })

    return dataframe, columns


def decode_dataframe(dataframe: DataFrame, columns: Dict[str, LabelCoder]):
    dataframe = dataframe.assign(**{
        cname: encoder.decode(dataframe[cname].values) for cname, encoder in columns.items()
    })

    return dataframe


def read_csv_and_encode(filepath, encode_columns: Union[List[str], Dict[str, LabelCoder]], chunksize: int = None, **kargs):
    if chunksize is None:
        dataframe = pd.read_csv(filepath, **kargs)
        dataframe, encode_columns = encode_dataframe(dataframe, encode_columns)
        return dataframe, encode_columns

    dataframe_chunks = []
    with pd.read_csv(filepath, iterator=True, chunksize=chunksize, ** kargs) as reader:
        reader: TextFileReader
        for dataframe in reader:
            dataframe, encode_columns = encode_dataframe(dataframe, encode_columns)
            dataframe_chunks.append(dataframe)

    ignore_index = ('index_col' not in kargs) or (not kargs['index_col'])
    dataframe: DataFrame = pd.concat(dataframe_chunks, ignore_index=ignore_index)
    return dataframe, encode_columns


def decode_and_write_csv(filepath, dataframe: DataFrame, encode_columns: Dict[str, LabelCoder], chunksize: int = None, **kargs):
    if chunksize is None:
        chunksize = len(dataframe)

    dataframe_list = np.array_split(dataframe, range(chunksize, len(dataframe), chunksize))
    dataframe = decode_dataframe(dataframe_list[0], encode_columns)
    dataframe.to_csv(filepath, **kargs)

    for dataframe in dataframe_list[1:]:
        dataframe = decode_dataframe(dataframe, encode_columns)
        dataframe.to_csv(filepath, header=False, mode='a', **kargs)
