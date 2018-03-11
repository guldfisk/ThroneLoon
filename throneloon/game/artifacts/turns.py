import typing as t

from throneloon.utils.containers.ring import Ring
from throneloon.game.artifacts.players import Player


class Turn(object):
	def __init__(self, player: Player):
		self._player = player

	@property
	def player(self):
		return self._player

	def __repr__(self) -> str:
		return '{}({})'.format(
			self.__class__.__name__,
			self._player,
		)


class TurnOrder(object):
	def __init__(self, players: t.Iterable[Player]):
		self._players = Ring(players) #type: Ring[Player]
		self._turn_log = [] #type: t.List[Turn]
		self._extra_turn_stack = [] #type: t.List[Turn]
		self._active_player = self._players.current() #type: Player

	@property
	def players(self) -> t.Sequence[Player]:
		return self._players.all

	@property
	def log(self) -> t.List[Turn]:
		return self._turn_log

	@property
	def active_player(self) -> Player:
		return self._active_player

	def current_turn(self) -> Turn:
		return  self._turn_log[-1]

	def add_extra_turn(self, turn: Turn) -> None:
		self._extra_turn_stack.append(turn)

	def next(self) -> Turn:
		turn = (
			self._extra_turn_stack.pop()
			if self._extra_turn_stack else
			Turn(self._players.next())
		)
		self._turn_log.append(turn)
		self._active_player = turn.player
		return turn

	def next_player(self) -> Player:
		return self._players.peek_next()

	def previous_player(self) -> Player:
		return self._players.peek_previous()

	def loop_from(self, player: Player) -> t.Iterable[Player]:
		return self._players.loop_from(player)

	def ap_nap(self) -> t.Iterable[Player]:
		return self.loop_from(self.active_player)

	def other_players(self, player: Player) -> t.Iterable[Player]:
		_iter = self._players.loop_from(player)
		next(_iter)
		return _iter