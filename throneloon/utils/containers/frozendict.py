import typing as t

from frozendict import frozendict

K = t.TypeVar('K')
V = t.TypeVar('V')

class FrozenDict(frozendict, t.Generic[K, V]):

	def __add__(self, other) -> 'FrozenDict[K, V]':
		return FrozenDict(self, **other)

	def __getitem__(self, key: K) -> V:
		return super().__getitem__(key)

	def __iter__(self) -> t.Iterable[K]:
		return super().__iter__()

	def items(self) -> t.AbstractSet[t.Tuple[K, V]]:
		return super().items()

	def values(self) -> t.AbstractSet[V]:
		return super().values()


