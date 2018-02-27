import typing as t

from abc import abstractmethod

from eventtree.replaceevent import Attributed, EventSession, Condition

from throneloon.game.artifacts.observation import Serializeable, GameObserver


class GameArtifact(Attributed):

	def __init__(self, session: EventSession):
		super().__init__(session)
		self._connected_conditions = [] #type: t.List[Condition]

	def connect_condition(self, condition: Condition):
		self._connected_conditions.append(condition)
		self._session.connect_condition(condition)

	def disconnect(self):
		while self._connected_conditions:
			self._session.disconnect_condition(
				self._connected_conditions.pop()
			)


class GameObject(GameArtifact, Serializeable):

	def visible(self, observer: GameObserver) -> bool:
		return True

	@abstractmethod
	def serialize(self, observer: GameObserver) -> str:
		return super().serialize(observer)
