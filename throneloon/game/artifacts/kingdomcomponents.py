import typing as t

from abc import abstractmethod, ABCMeta

from ordered_set import OrderedSet

from eventtree.replaceevent import Event

from throneloon.game.artifacts.artifact import GameObject, IdSession
from throneloon.game.artifacts.observation import GameObserver, serialization_values
from throneloon.game.artifacts.zones import Zone, ZoneFacingMode, ZoneOwner, Zoneable
from throneloon.game.artifacts.players import Player
from throneloon.game.values.currency import Price

from throneloon.utils.containers.frozendict import FrozenDict

class KingdomComponent(GameObject, metaclass=ABCMeta):
	name = 'Base Kingdom Component'

	@abstractmethod
	def setup(self, event: Event):
		pass

	def serialize(self, player: GameObserver) -> serialization_values:
		return FrozenDict(
			{
				'name': self.name,
			}
		)


class Pile(KingdomComponent, ZoneOwner):
	name = 'Abstract Base Pile'

	def __init__(self, session: IdSession, event: Event):
		super().__init__(session, event)

		self._zones = OrderedSet() #type: t.Set[Zone]

		self._cardboards = Zone(
			session = session,
			event = event,
			owner = self,
			facing_mode = ZoneFacingMode.STACK,
			ordered = True,
		)
		self._tokens = Zone(
			session = session,
			event = event,
			owner = self,
			facing_mode = ZoneFacingMode.FACE_UP,
			ordered = True,
		)

	@property
	def cardboards(self) -> Zone:
		return self._cardboards

	@property
	def tokens(self) -> Zone:
		return self._tokens

	@property
	def zones(self) -> 't.Set[Zone]':
		return self._zones

	@property
	def top_cardboard(self) -> t.Optional[Zoneable]:
		if self._cardboards:
			return self._cardboards[-1]
		else:
			return None

	def serialize(self, player: GameObserver) -> serialization_values:
		return super().serialize(player) + FrozenDict(
			{
				'type': 'Pile',
			}
		)

	def setup(self, event: Event):
		pass

	def __repr__(self) -> str:
		return self.__class__.__name__


class BuyableEvent(KingdomComponent):
	name = 'base buyable event'

	def __init__(self, session: IdSession, event: Event):
		super().__init__(session, event)

		self._price = None  # type: Price

	@property
	def price(self) -> Price:
		return self._price

	@abstractmethod
	def on_buy(self, event: Event):
		pass

	def serialize(self, player: GameObserver) -> serialization_values:
		return super().serialize(player) + FrozenDict(
			{
				'type': 'BuyableEvent',
			}
		)

	def setup(self, event: Event):
		pass


class Landmark(KingdomComponent):
	name = 'Base Landmark'

	def vp_value(self, player: Player) -> int:
		return 0

	def setup(self, event: Event):
		pass

	def serialize(self, player: GameObserver) -> serialization_values:
		return super().serialize(player) + FrozenDict(
			{
				'type': 'Landmark',
			}
		)
