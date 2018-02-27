import typing as t
import random

from abc import abstractmethod
from enum import Enum

from ordered_set import OrderedSet

from eventtree.replaceevent import EventSession

from throneloon.game.artifacts.observation import GameObserver
from throneloon.game.artifacts.artifact import GameObject, GameArtifact


class Zoneable(GameObject):
	def __init__(self, session: EventSession):
		super().__init__(session)
		self._zone = None #type: Zone

	@property
	def zone(self) -> 'Zone':
		return self._zone

	@abstractmethod
	def serialize(self, player: GameObserver) -> str:
		return super().serialize(player)


class ZoneOwner(object):

	@property
	@abstractmethod
	def zones(self) -> 't.Set[Zone]':
		pass

	def join(self, zone: 'Zone'):
		self.zones.add(zone)

class ZoneFacingMode(Enum):
	FACE_DOWN = 'face_down'
	FACE_UP = 'face_up'
	STACK = 'stack'

	# def default_face_up(self) -> bool:
	# 	return not self == ZoneFacingMode.FACE_DOWN

class Zone(GameObject):
	def __init__(
		self,
		session: EventSession,
		owner: ZoneOwner = None,
		facing_mode: ZoneFacingMode = ZoneFacingMode.FACE_DOWN,
		owner_see_face_down: bool = False,
		ordered: bool = True,
	):
		super().__init__(session)
		self._owner = owner #type: ZoneOwner
		if self._owner is not None:
			self._owner.join(self)
		self._facing_mode = facing_mode
		self._owner_see_face_down = owner_see_face_down
		self._ordered = ordered

		self._zoneables = [] #type: t.List[Zoneable]

	@property
	def owner(self) -> t.Optional[ZoneOwner]:
		return self._owner

	@property
	def facing_mode(self) -> ZoneFacingMode:
		return self._facing_mode

	@property
	def owner_see_face_down(self) -> bool:
		return self._owner_see_face_down

	@property
	def ordered(self) -> bool:
		return self._ordered

	def leave(self, zoneable: Zoneable) -> None:
		self._zoneables.remove(zoneable)

	def join(self, zoneable: Zoneable, index: t.Optional[int] = None):
		if zoneable.zone is not None:
			zoneable.zone.leave(zoneable)
		zoneable._zone = self
		if index is None:
			self._zoneables.append(zoneable)
		else:
			self._zoneables.insert(index, zoneable)

	def shuffle(self) -> None:
		random.shuffle(self._zoneables)

	def serialize(self, observer: GameObserver) -> str:
		return super().serialize(observer)

	def __iter__(self):
		return self._zoneables.__iter__()

	def __contains__(self, item):
		return self._zoneables.__contains__(item)

	def __getitem__(self, index):
		return self._zoneables.__getitem__(index)

	def __len__(self):
		return self._zoneables.__len__()