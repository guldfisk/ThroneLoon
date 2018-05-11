import typing as t

from ordered_set import OrderedSet

from collections import OrderedDict


class KingdomComponentInfo(object):
	def __init__(
		self,
		name: str,
		values: t.Dict[str, t.Any] = None,
	):
		self._name = name
		self._values = OrderedDict(values) if values else OrderedDict()

	@property
	def name(self) -> str:
		return self._name

	@property
	def values(self) -> t.Dict[str, t.Any]:
		return self._values

	# def __hash__(self):
	# 	return hash((self._name, self._values))
	#
	# def __eq__(self, other):
	# 	return (
	# 		isinstance(other, self.__class__)
	# 		and self._name == other.name
	# 		and self._values == other.values
	# 	)


class KingdomInfo(object):
	def __init__(
		self,
		piles: t.Iterable[KingdomComponentInfo] = None,
		events: t.Iterable[KingdomComponentInfo] = None,
		landmarks: t.Iterable[KingdomComponentInfo] = None,
		values: t.Dict[str, t.Any] = None,
	):
		self._piles = OrderedSet(piles) if piles is not None else OrderedSet()
		self._events = OrderedSet(events) if events is not None else OrderedSet()
		self._landmarks = OrderedSet(landmarks) if landmarks is not None else OrderedSet()
		self._values = OrderedDict(values) if values is not None else OrderedDict()

	@property
	def piles(self) -> t.Set[KingdomComponentInfo]:
		return self._piles

	@property
	def events(self)-> t.Set[KingdomComponentInfo]:
		return self._events

	@property
	def landmarks(self)-> t.Set[KingdomComponentInfo]:
		return self._landmarks

	@property
	def values(self) -> t.Dict[str, t.Any]:
		return self._values

	# def __hash__(self):
	# 	return hash((self._piles, self._events, self._landmarks, self._values))
	#
	# def __eq__(self, other):
	# 	return (
	# 		isinstance(other, self.__class__)
	# 		and self._piles == other.piles
	# 		and self._events == other.events
	# 		and self._landmarks == other.landmarks
	# 		and self._values == other.values
	# 	)
