import typing as t

from abc import abstractmethod

from eventtree.replaceevent import Event

from throneloon.game.game import Game
from throneloon.game.artifacts.kingdomcomponents import Pile
from throneloon.game.artifacts.cards import Card
from throneloon.game import gameevents as ge

class BasicSupplyPile(Pile):
	CARD_TYPE = None #type: t.Type[Card]

	def __init__(self, game: Game):
		super().__init__(game)
		self.name = self.CARD_TYPE.name

	def setup(self, event: Event):
		for _ in range(self._amount()):
			event.branch(
				ge.CreateCardboard,
				to = self._cardboards,
				card_type = self.CARD_TYPE
			).resolve()

	@abstractmethod
	def _amount(self) -> int:
		pass


class SupplyPile(BasicSupplyPile):

	def _amount(self) -> int:
		return 10