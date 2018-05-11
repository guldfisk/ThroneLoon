from abc import abstractmethod

from eventtree.replaceevent import Event

from throneloon.game.artifacts.zones import Zoneable
from throneloon.game.artifacts.observation import GameObserver, serialization_values


class EffectCard(Zoneable):

	@abstractmethod
	def receive(self, event: 'Event'):
		pass

	def serialize(self, player: GameObserver) -> serialization_values:
		return super().serialize(player)


class Boon(EffectCard):

	@abstractmethod
	def receive(self, event: 'Event'):
		pass


class Hex(EffectCard):

	@abstractmethod
	def receive(self, event: 'Event'):
		pass
