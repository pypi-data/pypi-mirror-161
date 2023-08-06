from typing import Any, Dict, Iterable, Union
import more_itertools


class VentureCodeSuffix:
    def __init__(self, venture_code) -> None:
        self.venture_code = venture_code

    def __call__(self, *args, **kwds) -> str:
        return f'__{self.venture_code}'


class DailyActionLogSuffix:
    def __init__(self, venture_code) -> None:
        self.venture_code = venture_code

    def __call__(self, re_replace=None, *args, **kwds) -> str:
        if re_replace is None or (date := re_replace.get(R'\$\(date\)')) is None:
            return f'__{self.venture_code}'
        return f'__{date}__{self.venture_code}'


ReDict = Union[Iterable[str], Dict[str, 'ReDict']]


class ParameterSuffix:
    def __init__(self, suffix_config: ReDict) -> None:
        self.suffix_config = suffix_config

    @staticmethod
    def extract_param(suffix_config: ReDict, kwds: ReDict):
        if isinstance(suffix_config, dict):
            params = [
                ParameterSuffix.extract_param(suffix_config[key], kwds[key]) for key in suffix_config
            ]
            params = list(more_itertools.flatten(params))
        else:
            params = [kwds[key] for key in suffix_config]

        return params

    def __call__(self, *_: Any, **kwds: ReDict) -> Any:
        params = self.extract_param(self.suffix_config, kwds)
        if len(params) == 0:
            return ''

        params = [''] + params
        return '__'.join(params)
