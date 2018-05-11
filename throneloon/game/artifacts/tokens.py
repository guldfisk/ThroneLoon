
from eventtree.replaceevent import Event

from throneloon.game.artifacts.artifact import IdSession
from throneloon.game.artifacts.zones import Zoneable
from throneloon.game.artifacts.observation import GameObserver, serialization_values
from throneloon.game.artifacts.victory import VictoryValuable

from throneloon.utils.containers.frozendict import FrozenDict


class Token(Zoneable, VictoryValuable):

	def __init__(self, session: IdSession, event: Event, name: str):
		super().__init__(session, event)
		self._name = name

	@property
	def name(self) -> str:
		return self._name

	def serialize(self, player: GameObserver) -> serialization_values:
		return super().serialize(player) + FrozenDict(
			{
				'name': self._name,
			}
		)

	@property
	def vp_value(self) -> int:
		return 0


class CoinToken(Token):
	pass