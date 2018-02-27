
from throneloon.game.artifacts.zones import Zoneable
from throneloon.game.artifacts.observation import GameObserver



class Token(Zoneable):

	def serialize(self, player: GameObserver) -> str:
		return super().serialize(player)