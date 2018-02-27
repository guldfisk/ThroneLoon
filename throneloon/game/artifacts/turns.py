import typing as t

from throneloon.utils.containers.ring import Ring
from throneloon.game.artifacts.players import Player


class Turn(object):
	def __init__(self, player: Player):
		self._player = player

	@property
	def player(self):
		return self._player


class TurnOrder(object):
	def __init__(self, players: t.Iterable[Player]):
		self._players = Ring(players)
		self._turn_log = [] #type: t.List[Turn]
		self._extra_turn_stack = [] #type: t.List[Turn]

	@property
	def players(self) -> t.Sequence[Player]:
		return self._players.all

	def add_extra_turn(self, turn: Turn) -> None:
		self._extra_turn_stack.append(turn)

	def next(self) -> Turn:
		turn = (
			self._extra_turn_stack.pop()
			if self._extra_turn_stack else
			Turn(self._players.next())
		)
		self._turn_log.append(turn)
		return turn

	def next_player(self) -> Player:
		return self._players.peek_next()

	def previous_player(self) -> Player:
		return self._players.peek_previous()
