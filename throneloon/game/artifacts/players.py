import typing as t

from ordered_set import OrderedSet

from eventtree.replaceevent import EventSession

from throneloon.game.artifacts.artifact import GameObject
from throneloon.game.artifacts.mats import Mat
from throneloon.game.artifacts.observation import GameObserver
from throneloon.game.artifacts.zones import Zone, ZoneOwner, ZoneFacingMode
from throneloon.game.values.currency import CurrencyValue


class Player(GameObject, ZoneOwner):
	def __init__(self, session: EventSession):
		super().__init__(session)

		self._zones = OrderedSet() #type: t.Set[Zone]

		self._currency = CurrencyValue()
		self.actions = 0
		self.buys = 0

		self._mats = {} #type: t.Dict[str, Mat]

		self._library = Zone(
			session = session,
			owner = self,
			facing_mode = ZoneFacingMode.FACE_DOWN,
			owner_see_face_down = False,
			ordered = True,
		)
		self._hand = Zone(
			session = session,
			owner = self,
			facing_mode = ZoneFacingMode.FACE_DOWN,
			owner_see_face_down = True,
			ordered = False,
		)
		self._battlefield = Zone(
			session = session,
			owner = self,
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		)
		self._graveyard = Zone(
			session = session,
			owner = self,
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		)

		self._tokens = Zone(
			session = session,
			owner = self,
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		)
		self._states = Zone(
			session = session,
			owner = self,
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		)

	@property
	def zones(self) -> 't.Set[Zone]':
		return self._zones

	@property
	def currency(self) -> CurrencyValue:
		return self._currency

	@currency.setter
	def currency(self, value: CurrencyValue) -> None:
		self._currency = value

	@property
	def mats(self) -> t.Dict[str, Mat]:
		return self._mats

	@property
	def library(self) -> Zone:
		return self._library

	@property
	def hand(self) -> Zone:
		return self._hand

	@property
	def battlefield(self) -> Zone:
		return self._battlefield

	@property
	def graveyard(self) -> Zone:
		return self._graveyard

	@property
	def tokens(self) -> Zone:
		return self._tokens

	@property
	def states(self) -> Zone:
		return self._states

	def serialize(self, observer: GameObserver) -> str:
		return super().serialize(observer)

