import typing as t

from abc import abstractmethod

from eventtree.replaceevent import Event, Replacement

from throneloon.game.game import Game
from throneloon.game.artifacts.kingdomcomponents import Pile
from throneloon.game.artifacts.cards import Card
from throneloon.game import gameevents as ge

class BasicSupplyPile(Pile):
	CARD_TYPE = None #type: t.Type[Card]

	def __init__(self, game: Game, event: ge.CreatePile):
		super().__init__(game, event)
		self.name = self.CARD_TYPE.name

	def setup(self, event: ge.CreatePile):
		for _ in range(self._amount(event)):
			event.branch(
				ge.CreateCardboard,
				to = self._cardboards,
				card_type = self.CARD_TYPE,
			)

	@abstractmethod
	def _amount(self, event: ge.CreatePile) -> int:
		pass


class SupplyPile(BasicSupplyPile):

	def _amount(self, event: ge.CreatePile) -> int:
		return 10


class VictorySupplyPile(BasicSupplyPile):

	def _amount(self, event: ge.CreatePile) -> int:
		return 12 if len(event._session.players) > 2 else 8


class HeirloomPile(SupplyPile):
	HEIRLOOM_TYPE = None #type: t.Type[Card]

	def setup(self, event: ge.CreatePile):
		super().setup(event)
		self.create_condition(
			Replacement,
			parent = event,
			trigger = 'CreateStartLibrary',
			replace = self._inject_heirloom,
		)

	def _inject_heirloom(self, event: ge.CreateStartLibrary):
		if 'Copper' in event.content:
			event.content[event.content.index('Copper')] = self.HEIRLOOM_TYPE
		event.resolve()
