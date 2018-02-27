
from throneloon.game.artifacts.observation import GameObserver
from throneloon.game.artifacts.zones import Zoneable


class State(Zoneable):

	def serialize(self, player: GameObserver) -> str:
		return super().serialize(player)