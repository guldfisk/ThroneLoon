import typing as t

from abc import abstractmethod

from weakreflist import WeakList

from eventtree.replaceevent import Attributed, EventSession, Condition, Event

from throneloon.game.artifacts.observation import Serializeable, GameObserver
from throneloon.game.idprovide import IdProviderInterface


class GameArtifact(Attributed):

	def __init__(self, session: EventSession, event: Event):
		super().__init__(session)
		self._connected_conditions = WeakList()

	def create_condition(self, condition_type: t.Type[Condition], parent: Event, **kwargs):
		self._connected_conditions.append(
			self._session.create_condition(
				condition_type = condition_type,
				parent = parent,
				source = self,
				**kwargs,
			)
		)

	def disconnect(self, parent: Event):
		while self._connected_conditions:
			self._session.disconnect_condition(
				condition = self._connected_conditions.pop(-1)(),
				parent = parent,
			)


class IdSession(EventSession, IdProviderInterface):
	pass


class GameObject(GameArtifact, Serializeable):

	def __init__(self, session: IdSession, event: Event):
		super().__init__(session, event)
		self._id = session.get_id()

	def visible(self, observer: GameObserver) -> bool:
		return True

	@abstractmethod
	def serialize(self, observer: GameObserver) -> str:
		return super().serialize(observer)
