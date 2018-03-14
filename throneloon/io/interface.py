import typing as t

from abc import ABCMeta, abstractmethod

from eventtree.replaceevent import Event, Condition

from throneloon.game.artifacts.observation import GameObserver
from throneloon.game.artifacts.artifact import GameArtifact

io_option = t.Union[GameArtifact, Condition, str]
io_options = t.Iterable[io_option]
io_additional_options = t.Optional[t.Dict[io_option, t.Optional[str]]]

class IOInterface(object, metaclass=ABCMeta):

	@abstractmethod
	def bind_players(self, players: t.List[GameObserver]) -> None:
		pass

	@abstractmethod
	def select_option(
		self,
		player: GameObserver,
		options: io_options,
		optional: bool = False,
		additional_options: io_additional_options = None,
		reason: t.Optional[str] = None,
	) -> io_option:
		pass

	@abstractmethod
	def select_options(
		self,
		player: GameObserver,
		options: io_options,
		minimum: t.Optional[int] = 1,
		maximum: t.Optional[int] = None,
		additional_options: io_additional_options = None,
		reason: t.Optional[str] = None,
	) -> t.List[io_option]:
		pass

	@abstractmethod
	def notify_event(self, event: Event) -> None:
		pass