import typing as t
from abc import ABCMeta

from eventtree.replaceevent import EventSession, Event

from throneloon.game.artifacts.observation import GameObserver
from throneloon.game.artifacts.artifact import GameArtifact
from throneloon.game.artifacts.zones import Zoneable, ZoneOwner
from throneloon.game.artifacts.kingdomcomponents import Pile
from throneloon.game.values.cardtypes import TypeLine
from throneloon.game.values.currency import Price


class Card(GameArtifact, metaclass=ABCMeta):
	name = 'abstract_base_card'

	def __init__(
		self,
		session: EventSession,
		cardboard: 'Cardboard'
	):
		super().__init__(session)
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

	def on_play(self, event: Event):
		pass

	def on_game_end(self, event: Event):
		pass


class Cardboard(Zoneable):
	def __init__(
		self,
		session: EventSession,
		card_type: t.Type[Card],
		origin_pile: 'Pile' = None,
		face_up: bool = True,
	):
		super().__init__(session)
		self._printed_card_type = card_type
		self._origin_pile = origin_pile
		self._face_up = face_up

		self._card = card_type(session, self)

		self.id_map = None #type: t.Dict[GameObserver, t.Optional[str]]

	@property
	def printed_card_type(self) -> t.Type[Card]:
		return self._printed_card_type

	@property
	def origin_pile(self) -> 't.Optional[Pile]':
		return self._origin_pile

	@property
	def card(self) -> Card:
		return self._card

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

	def visible(self, player) -> bool:
		return (
			self._face_up
			or player == self._zone.owner and self._zone.owner_see_face_down
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

	def on_play(self, event: Event):
		self._card.on_play(event)

	def on_game_end(self, event: Event):
		self._card.on_game_end(event)

	def serialize(self, observer: GameObserver) -> str:
		return super().serialize(observer)

	def __repr__(self):
		return '{}({}, {})'.format(
			self.__class__.__name__,
			self.name,
			id(self),
		)