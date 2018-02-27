from abc import abstractmethod

from eventtree.replaceevent import Event

from throneloon.game.artifacts.zones import Zoneable
from throneloon.game.artifacts.observation import GameObserver


class EffectCard(Zoneable):

	@abstractmethod
	def receive(self, event: 'Event'):
		pass

	def serialize(self, player: GameObserver) -> str:
		return super().serialize(player)


class Boon(EffectCard):

	@abstractmethod
	def receive(self, event: 'Event'):
		pass


class Hex(EffectCard):

	@abstractmethod
	def receive(self, event: 'Event'):
		pass
