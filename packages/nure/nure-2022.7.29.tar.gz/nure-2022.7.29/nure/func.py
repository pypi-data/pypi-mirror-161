from typing import Any, Callable, Iterable


class Chain:
    def __init__(self, *l_func: Iterable[Callable]) -> None:
        self.l_func = l_func

    def __call__(self, argument: Any) -> Any:
        for func in self.l_func:
            argument = func(argument)

        return argument


class FromIterable:
    def __init__(self, func: Callable) -> None:
        self.func = func

    def __call__(self, iterable_arguments: Iterable):
        return self.func(*iterable_arguments)
