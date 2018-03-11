import typing as t

from abc import ABCMeta, abstractmethod

from eventtree.replaceevent import Event, Condition

from throneloon.game.artifacts.observation import GameObserver
from throneloon.game.artifacts.artifact import GameArtifact


class IOInterface(object, metaclass=ABCMeta):

	@abstractmethod
	def select_option(
		self,
		player: GameObserver,
		options: t.Iterable[t.Union[GameArtifact, str, Condition]],
		optional: bool = False,
		additional_options: t.Optional[t.Dict[t.Union[GameArtifact, str, Condition], t.Optional[str]]] = None,
		reason: t.Optional[str] = None,
	) -> t.Union[GameArtifact, str, Condition]:
		pass

	@abstractmethod
	def select_options(
		self,
		player: GameObserver,
		options: t.Iterable[t.Union[GameArtifact, str, Condition]],
		minimum: t.Optional[int] = 1,
		maximum: t.Optional[int] = None,
		additional_options: t.Optional[t.Dict[t.Union[GameArtifact, str, Condition], t.Optional[str]]] = None,
		reason: t.Optional[str] = None,
	) -> t.Union[t.List[t.Union[GameArtifact, str]], t.Union[GameArtifact, str, Condition]]:
		pass

	@abstractmethod
	def notify_event(self, event: Event) -> None:
		pass