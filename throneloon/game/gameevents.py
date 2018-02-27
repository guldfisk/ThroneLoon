import typing as t

import random

from eventtree.replaceevent import Event, EventCheckException

from throneloon.game.artifacts.turns import TurnOrder
from throneloon.game.artifacts.cards import Cardboard, Card
from throneloon.game.artifacts.kingdomcomponents import Pile
from throneloon.game.artifacts.observation import Serializeable, GameObserver
from throneloon.game.artifacts.players import Player
from throneloon.game.artifacts.zones import Zone, Zoneable, ZoneFacingMode
from throneloon.game.game import Game
from throneloon.game.idprovide import IdProvider
from throneloon.game.setup.setupinfo import SetupInfo
from throneloon.game.values.currency import CurrencyValue
from throneloon.models import models


class GameEvent(Event, Serializeable):

	@property
	def game(self) -> Game:
		return self._session

	def serialize(self, player: GameObserver) -> str:
		return super().serialize(player)


class CreateZoneable(GameEvent):

	@property
	def target(self) -> Zoneable:
		return self._values['target']

	@target.setter
	def target(self, zoneable: Zoneable) -> None:
		self._values['target'] = zoneable

	@property
	def to(self) -> Zone:
		return self._values['to']

	@to.setter
	def to(self, zone: Zone) -> None:
		self._values['to'] = zone

	def payload(self, **kwargs):
		self.to.join(self.target)
		return self.target


class CreateCardboard(GameEvent):

	@property
	def to(self) -> Zone:
		return self._values['to']

	@to.setter
	def to(self, zone: Zone) -> None:
		self._values['to'] = zone

	@property
	def card_type(self) -> t.Type[Card]:
		return self._values['card_type']

	@card_type.setter
	def card_type(self, card_type: t.Type[Card]) -> None:
		self._values['card_type'] = card_type

	@property
	def face_up(self) -> bool:
		return self._values['face_up']

	@face_up.setter
	def face_up(self, face_up: bool) -> None:
		self._values['face_up'] = face_up

	def setup(self, **kwargs):
		self._values.setdefault('face_up', None)

	def payload(self, **kwargs):
		cardboard = self.spawn_tree(
			CreateZoneable,
			target = Cardboard(
				session = self._session,
				card_type = self.card_type,
				origin_pile = self.to if isinstance(self.to.owner, Pile) else None,
				face_up = self.to.facing_mode != ZoneFacingMode.FACE_DOWN,
			)
		).resolve() #type: t.Optional[Cardboard]
		if cardboard is not None:
			if self.to.facing_mode == ZoneFacingMode.STACK and len(self.to) >= 2 and self.to[-1] == cardboard:
				self.branch(TurnCardboard, face_up=False, target=self.to[-2]).resolve()
			if cardboard.zone.ordered:
				cardboard.id_map = {
					player: self._session.id_provider.get_id()
					for player in
					self.game.players
				}
			else:
				cardboard.id_map = {
					player:
						self._session.id_provider.get_id()
						if cardboard.visible(player) else
						None
					for player in
					cardboard.id_map
				}


class MoveZoneable(GameEvent):

	@property
	def target(self) -> Zoneable:
		return self._values['target']

	@target.setter
	def target(self, zoneable: Zoneable) -> None:
		self._values['target'] = zoneable

	@property
	def frm(self) -> Zone:
		return self._values['frm']

	@frm.setter
	def frm(self, zone: Zone) -> None:
		self._values['frm'] = zone

	@property
	def to(self) -> Zone:
		return self._values['to']

	@to.setter
	def to(self, zone: Zone) -> None:
		self._values['to'] = zone

	@property
	def index(self) -> int:
		return self._values['index']

	@index.setter
	def index(self, value: int) -> None:
		self._values['index'] = value

	def setup(self, **kwargs):
		self._values.setdefault('index', None)

	def check(self, **kwargs):
		if not self.target in self.frm:
			raise EventCheckException()

	def payload(self, **kwargs):
		self.to.join(self.target, self.index)
		return self.target


class TurnCardboard(GameEvent):

	@property
	def target(self) -> Cardboard:
		return self._values['target']

	@target.setter
	def target(self, cardboard: Cardboard) -> None:
		self._values['target'] = cardboard

	@property
	def face_up(self) -> bool:
		return self._values['face_up']

	@face_up.setter
	def face_up(self, face_up: bool) -> None:
		self._values['face_up'] = face_up

	def payload(self, **kwargs):
		self.target.face_up = self.face_up

	def check(self, **kwargs):
		if self.target.face_up == self.face_up:
			raise EventCheckException()


class MoveCardboard(GameEvent):

	@property
	def target(self) -> Cardboard:
		return self._values['target']

	@target.setter
	def target(self, cardboard: Cardboard) -> None:
		self._values['target'] = cardboard

	@property
	def frm(self) -> Zone:
		return self._values['frm']

	@frm.setter
	def frm(self, zone: Zone) -> None:
		self._values['frm'] = zone

	@property
	def to(self) -> Zone:
		return self._values['to']

	@to.setter
	def to(self, zone: Zone) -> None:
		self._values['to'] = zone

	@property
	def index(self) -> int:
		return self._values['index']

	@index.setter
	def index(self, value: int) -> None:
		self._values['index'] = value

	@property
	def face_up(self) -> bool:
		return self._values['face_up']

	@face_up.setter
	def face_up(self, face_up: bool) -> None:
		self._values['face_up'] = face_up

	def setup(self, **kwargs):
		self._values.setdefault('face_up', None)
		self._values.setdefault('index', None)

	def payload(self, **kwargs):
		previous_visibility = {player: self.target.visible(player) for player in self.target.id_map}
		cardboard = self.spawn_tree(MoveZoneable) #type: Cardboard
		if cardboard:
			if self.face_up is not None:
				self.spawn_tree(TurnCardboard)
			else:
				if self.to.facing_mode == ZoneFacingMode.STACK and len(self.to) >= 2 and self.target == self.to[-1]:
					self.branch(TurnCardboard, target = self.to[-2], face_up = False).resolve()
				if self.frm.facing_mode == ZoneFacingMode.STACK and self.frm:
					self.branch(TurnCardboard, target = self.frm[-1], face_up = True).resolve()
			if self.frm.ordered == False and self.to.ordered == True:
				for player in cardboard.id_map:
					if not cardboard.visible(player):
						cardboard.id_map[player] = None
			elif self.frm.ordered == True and self.to.ordered == False:
				for player in cardboard.id_map:
					if not previous_visibility[player]:
						cardboard.id_map[player] = self._session.id_provider.get_id()
			return cardboard


class CreatePile(GameEvent):

	@property
	def pile_type(self):
		return self._values['pile_type']

	@pile_type.setter
	def pile_type(self, pile_type: t.Type[Pile]):
		self._values['pile_type'] = pile_type

	@property
	def in_supply(self) -> bool:
		return self._values['in_supply']

	@in_supply.setter
	def in_supply(self, in_supply: bool):
		self._values['in_supply'] = in_supply

	@property
	def setup_values(self) -> t.Dict[str, t.Any] :
		return self._values['setup_values']

	def check(self, **kwargs):
		self._values.setdefault('setup_values', dict())
		self._values.setdefault('in_supply', True)

	def payload(self, **kwargs):
		pile = self.pile_type(self.game)
		if self.in_supply:
			self.game.supply_piles[pile.name] = pile
		else:
			self.game.non_supply_piles[pile.name] = pile
		pile.setup(self)


class Setup(GameEvent):

	@property
	def info(self) -> SetupInfo:
		return self._values['info']

	@property
	def seed(self) -> t.Optional[t.ByteString]:
		return self._values['seed']

	@seed.setter
	def seed(self, value: t.Optional[t.ByteString]):
		self._values['seed'] = value

	def setup(self, **kwargs):
		self._values.setdefault('seed', None)

	def payload(self, **kwargs):
		if self.seed is not None:
			random.seed(self.seed)
		else:
			random.seed()
		self.game.id_provider = IdProvider(str(random.random()).encode('ASCII'))
		self.game.turn_order = TurnOrder(Player(self.game) for _ in range(self.info.num_players))
		for key, value in models.BASIC_SUPPLY.items():
			self.branch(CreatePile, pile_type=value).resolve()
		for pile_info in self.info.kingdom_info.piles:
			pile_type = models.ALL_PILES.get(pile_info.name)
			if pile_type:
				self.branch(CreatePile, pile_type=pile_type, setup_values=pile_info.values).resolve()

class ShuffleZone(GameEvent):

	@property
	def player(self) -> Player:
		return self._values['player']

	@player.setter
	def player(self, player: Player) -> None:
		self._values['player'] = player

	@property
	def to(self) -> Zone:
		return self._values['to']

	@to.setter
	def to(self, zone: Zone) -> None:
		self._values['to'] = zone

	def setup(self, **kwargs):
		self._values.setdefault('player', None)
		if self.player is not None:
			self._values.setdefault('to', self.player.library)

	def check(self, **kwargs):
		if not self.to.ordered:
			raise EventCheckException()

	def payload(self, **kwargs):
		if self.to.facing_mode == ZoneFacingMode.STACK:
			for cardboard in self.to:
				self.branch(TurnCardboard, target=cardboard, face_up=False).resolve()
		for cardboard in self.to:
			for observer in cardboard.id_map:
				cardboard.id_map[observer] = self.game.id_provider.get_id()
		self.to.shuffle()
		if self.to.facing_mode == ZoneFacingMode.STACK:
			self.branch(TurnCardboard, target=self.to[-1], face_up=True).resolve()


class AddCurrency(GameEvent):

	@property
	def player(self) -> Player:
		return self._values['player']

	@player.setter
	def player(self, player: Player) -> None:
		self._values['player'] = player

	@property
	def amount(self) -> CurrencyValue:
		return self._values['amount']

	@amount.setter
	def amount(self, amount: CurrencyValue) -> None:
		self._values['amount'] = amount

	def payload(self, **kwargs):
		self.player.currency += self.amount


class ResolveCardboard(GameEvent):

	@property
	def target(self) -> Cardboard:
		return self._values['target']

	@target.setter
	def target(self, cardboard: Cardboard) -> None:
		self._values['cardboard'] = cardboard

	@property
	def player(self) -> Player:
		return self._values['player']

	@player.setter
	def player(self, player: Player) -> None:
		self._values['player '] = player

	def payload(self, **kwargs):
		self.target.on_play(self)


class AddAction(GameEvent):

	@property
	def player(self) -> Player:
		return self._values['player']

	@player.setter
	def player(self, player: Player) -> None:
		self._values['player'] = player

	@property
	def amount(self) -> int:
		return self._values['amount']

	@amount.setter
	def amount(self, amount: int) -> None:
		self._values['amount'] = amount

	def payload(self, **kwargs):
		self.player.actions += self.amount