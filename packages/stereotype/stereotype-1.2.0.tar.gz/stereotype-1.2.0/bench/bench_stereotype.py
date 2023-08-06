from __future__ import annotations

from typing import List, Optional

from stereotype import Model, StrField, ListField
from bench.common import benchmark_cpu, memory_bench


class BaseStuff(Model):
    name: str = StrField(min_length=2)
    flag: bool = False


class ListStuff(BaseStuff):
    stuff: Stuff
    list: List[str] = ListField(min_length=1)


class ModelStuff(Model):
    value: float
    def_value: float = 4.2


class Stuff(BaseStuff):
    optional: Optional[int] = None
    strange: Optional[float] = 4.7
    model: ModelStuff
    items: List[ListStuff] = list

    def validate_flag(self, value: bool, _):
        if not value and self.optional is None:
            raise ValueError('Must be true if optional is not set')


if __name__ == '__main__':
    def benchmark(inputs: List[dict], validate: bool):
        for data in inputs:
            model = Stuff(data)
            if validate:
                model.validate()
            yield model.to_primitive()

    benchmark_cpu(benchmark, depth=4, validate=True)
    # memory_bench(Stuff, lambda model: model.to_primitive(), 10000, 4)  # 349MB
