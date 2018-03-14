
from throneloon.game.artifacts.zones import Zoneable
from throneloon.game.artifacts.observation import GameObserver
from throneloon.game.artifacts.victory import VictoryValuable


class Token(Zoneable, VictoryValuable):

	def serialize(self, player: GameObserver) -> str:
		return super().serialize(player)

	@property
	def vp_value(self) -> int:
		return 0


class CoinToken(Token):
	pass