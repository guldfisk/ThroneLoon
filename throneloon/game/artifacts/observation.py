import typing as t

from abc import ABCMeta, abstractmethod

from throneloon.utils.containers.frozendict import FrozenDict


class GameObserver(object):

	@property
	@abstractmethod
	def peeking(self) -> t.List[object]:
		pass


class Serializeable(object, metaclass=ABCMeta):

	@abstractmethod
	def serialize(self, player: GameObserver) -> 'serialization_values':
		return FrozenDict({'type': self.__class__.__name__})


serialization_value = t.Union[int, str, bool, None, Serializeable]
serialization_values = FrozenDict[str, serialization_value]
