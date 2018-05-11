import typing as t
import random

from abc import abstractmethod
from enum import Enum
from itertools import chain

from eventtree.replaceevent import Event

from throneloon.game.artifacts.observation import GameObserver, serialization_values, Serializeable
from throneloon.game.artifacts.artifact import GameObject, IdSession

from throneloon.utils.containers.frozendict import FrozenDict


class Zoneable(GameObject):
	def __init__(self, session: IdSession, event: Event):
		super().__init__(session, event)
		self._zone = None #type: Zone

	@property
	def zone(self) -> 'Zone':
		return self._zone

	@property
	def owner(self) -> 't.Optional[ZoneOwner]':
		return self._zone.owner

	@abstractmethod
	def serialize(self, player: GameObserver) -> serialization_values:
		return super().serialize(player)


class ZoneOwner(Serializeable):

	@property
	@abstractmethod
	def zones(self) -> 't.Set[Zone]':
		pass

	@property
	def zoneables(self) -> t.Iterable[Zoneable]:
		return chain(*self.zones)

	def join(self, zone: 'Zone'):
		self.zones.add(zone)


class ZoneFacingMode(Enum):
	FACE_DOWN = 'face_down'
	FACE_UP = 'face_up'
	STACK = 'stack'


Z = t.TypeVar('Z', covariant=True, bound=Zoneable)


class Zone(t.Generic[Z], GameObject):

	def __init__(
		self,
		session: IdSession,
		event: Event,
		owner: ZoneOwner = None,
		name: str = None,
		facing_mode: ZoneFacingMode = ZoneFacingMode.FACE_DOWN,
		owner_see_face_down: bool = False,
		ordered: bool = True,
	):
		super().__init__(session, event)
		self._owner = owner #type: ZoneOwner

		self._name = name

		if self._owner is not None:
			self._owner.join(self)

		self._facing_mode = facing_mode
		self._owner_see_face_down = owner_see_face_down
		self._ordered = ordered

		self._zoneables = [] #type: t.List[Z]

	@property
	def owner(self) -> t.Optional[ZoneOwner]:
		return self._owner

	@property
	def name(self) -> str:
		return self._name

	@property
	def facing_mode(self) -> ZoneFacingMode:
		return self._facing_mode

	@property
	def owner_see_face_down(self) -> bool:
		return self._owner_see_face_down

	@property
	def ordered(self) -> bool:
		return self._ordered

	def leave(self, zoneable: Z) -> None:
		self._zoneables.remove(zoneable)

	def join(self, zoneable: Z, index: t.Optional[int] = None) -> None:
		if zoneable.zone is not None:
			zoneable.zone.leave(zoneable)
		zoneable._zone = self
		if index is None:
			self._zoneables.append(zoneable)
		else:
			self._zoneables.insert(index, zoneable)

	def shuffle(self, to: t.Optional[int] = None) -> None:
		if to is None:
			random.shuffle(self._zoneables)
		else:
			self._zoneables[:to] = random.sample(
				self._zoneables[:to],
				to if to >= 0 else len(self._zoneables) + to
			)

	def serialize(self, player: GameObserver) -> serialization_values:
		return super().serialize(player) + FrozenDict(
			{
				'name': self._name,
				'owner': self._owner,
				'ordered': self._ordered,
			}
		)

	def __iter__(self) -> t.Iterable[Z]:
		return self._zoneables.__iter__()

	def __contains__(self, item: Z) -> bool:
		return self._zoneables.__contains__(item)

	def __getitem__(self, index):
		return self._zoneables.__getitem__(index)

	def __len__(self) -> int:
		return self._zoneables.__len__()

	def __repr__(self) -> str:
		return '{}({}, {})'.format(
			self.__class__.__name__,
			self.name,
			self.owner,
		)

