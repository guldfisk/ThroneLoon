import typing as t

from abc import ABCMeta, abstractmethod

from eventtree.replaceevent import Event

from throneloon.artifacts.players.player import Player
from throneloon.artifacts.artifact import GameArtifact

class IOInterface(object, metaclass=ABCMeta):

	@abstractmethod
	def select_option(
		self,
		player: Player,
		options: t.Iterable[t.Union[GameArtifact, str]],
		reason: str = None,
	) -> t.Union[GameArtifact, str]:
		pass

	@abstractmethod
	def notify_event(self, event: Event) -> None:
		pass