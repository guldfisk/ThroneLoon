import typing as t

from throneloon.game.setup.kingdominfo import KingdomInfo

class SetupInfo(object):
	def __init__(
		self,
		kingdom_info: KingdomInfo = None,
		num_players: int = 2,
	):
		self._kingdom_info = kingdom_info if kingdom_info is not None else KingdomInfo()
		self._num_players = num_players

	@property
	def kingdom_info(self) -> KingdomInfo:
		return self._kingdom_info

	@property
	def num_players(self) -> int:
		return self._num_players

	def __hash__(self):
		return hash((self._kingdom_info, self._num_players))

	def __eq__(self, other):
		return (
			isinstance(other, self.__class__)
			and self._kingdom_info == other.kingdom_info
			and self._num_players == other.num_players
		)