import typing as t
from abc import ABCMeta

from eventtree.replaceevent import EventSession, Event

from throneloon.game.artifacts.observation import GameObserver, serialization_values
from throneloon.game.artifacts.artifact import GameArtifact
from throneloon.game.artifacts.zones import Zoneable, ZoneOwner, IdSession, Zone
from throneloon.game.artifacts.victory import VictoryValuable
from throneloon.game.values.cardtypes import TypeLine
from throneloon.game.values.currency import Price

from throneloon.utils.containers.frozendict import FrozenDict


class Card(GameArtifact, VictoryValuable, metaclass=ABCMeta):
	name = 'abstract_base_card'

	def __init__(
		self,
		session: EventSession,
		cardboard: 'Cardboard',
		event: Event,
	):
		super().__init__(session, event)
		self._cardboard = cardboard

		self._price = None #type: Price
		self._type_line = TypeLine(())

	@property
	def cardboard(self) -> 'Cardboard':
		return self._cardboard

	@property
	def price(self) -> Price:
		return self._price

	@property
	def type_line(self) -> TypeLine:
		return self._type_line

	@property
	def vp_value(self) -> int:
		return 0

	def need_tre(self, event: Event) -> bool:
		return False

	def on_play(self, event: Event):
		pass

	def attack(self, event: Event):
		pass


class Cardboard(Zoneable, VictoryValuable):

	def __init__(
		self,
		session: IdSession,
		card_type: t.Type[Card],
		event: Event,
		origin_zone: Zone = None,
		face_up: bool = True,
	):
		super().__init__(session, event)
		self._printed_card_type = card_type
		self._origin_zone = origin_zone
		self._face_up = face_up

		self._card = card_type(session, self, event)

		self.id_map = None #type: t.Dict[GameObserver, t.Optional[str]]

		self._attachments = [] #type: t.List[Cardboard]

	@property
	def printed_card_type(self) -> t.Type[Card]:
		return self._printed_card_type

	@property
	def origin_zone(self) -> 't.Optional[Zone]':
		return self._origin_zone

	@property
	def card(self) -> Card:
		return self._card

	@card.setter
	def card(self, card: Card) -> None:
		self._card = card

	@property
	def name(self):
		return self._card.name

	@property
	def face_up(self) -> bool:
		return self._face_up

	@face_up.setter
	def face_up(self, face_up: bool) -> None:
		self._face_up = face_up

	@property
	def owner(self) -> t.Optional[ZoneOwner]:
		return self._zone.owner

	@property
	def attachments(self) -> 't.List[Cardboard]':
		return self._attachments

	def visible(self, observer: GameObserver) -> bool:
		return (
			self._face_up
			or observer == self._zone.owner and self._zone.owner_see_face_down
			or self in observer.peeking
		)

	def flip(self) -> bool:
		self._face_up = not self._face_up
		return self._face_up

	@property
	def price(self) -> Price:
		return self._card.price

	@property
	def type_line(self) -> TypeLine:
		return self._card.type_line

	@property
	def vp_value(self) -> int:
		return self._card.vp_value

	def on_play(self, event: Event):
		self._card.on_play(event)

	def attack(self, event: Event):
		self._card.attack(event)

	def need_tre(self, event: Event) -> bool:
		return self._card.need_tre(event)

	def serialize(self, player: GameObserver) -> serialization_values:
		return (
			super().serialize(player) + FrozenDict(
				{
					'printed_card_type': self._printed_card_type.name,
					'card_type': self._card.name,
					'face_up': self._face_up,
					'id': self.id_map[player],
				}
			) if self.visible(player) else
			super().serialize(player) + FrozenDict(
				{
					'face_up': self._face_up,
					'id': self.id_map[player],
				}
			)
		)

	def __repr__(self):
		return '{}({}, {})'.format(
			self.__class__.__name__,
			self.name
			if self.name == self.printed_card_type.name else
			'{}({})'.format(
				self.printed_card_type.name,
				self.name,
			),
			id(self),
		)