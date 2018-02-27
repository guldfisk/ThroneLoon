
from throneloon.game.artifacts.zones import Zone
from throneloon.game.artifacts.observation import GameObserver

class Mat(Zone):

	def serialize(self, player: GameObserver) -> str:
		return super().serialize(player)