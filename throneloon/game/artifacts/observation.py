import json

from abc import ABCMeta, abstractmethod


class GameObserver(object):
	pass


class Serializeable(object, metaclass=ABCMeta):

	@abstractmethod
	def serialize(self, player: GameObserver) -> str:
		return json.dumps({'type': self.__class__.__name__})
