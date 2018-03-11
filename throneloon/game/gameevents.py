import typing as t

import random

from eventtree.replaceevent import Event, EventCheckException, Replacement, EventResolutionException

from throneloon.game.artifacts.turns import TurnOrder, Turn
from throneloon.game.artifacts.cards import Cardboard, Card
from throneloon.game.artifacts.kingdomcomponents import Pile, BuyableEvent, Landmark
from throneloon.game.artifacts.observation import Serializeable, GameObserver
from throneloon.game.artifacts.players import Player, AdditionalOptionTreatment
from throneloon.game.artifacts.zones import Zone, Zoneable, ZoneFacingMode
from throneloon.game.game import Game
from throneloon.game.idprovide import IdProvider
from throneloon.game.setup.setupinfo import SetupInfo
from throneloon.game.values.currency import CurrencyValue
from throneloon.game.values.cardtypes import CardType, TypeLine


class GameEvent(Event, Serializeable):

	@property
	def game(self) -> Game:
		return self._session

	@property
	def player(self) -> t.Optional[Player]:
		return self._values['player']

	@player.setter
	def player(self, player: Player) -> None:
		self._values['player'] = player

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
				event = self,
				origin_zone= self.to if isinstance(self.to.owner, Pile) else None,
				face_up = self.to.facing_mode != ZoneFacingMode.FACE_DOWN,
			)
		) #type: t.Optional[Cardboard]

		if cardboard is None:
			raise EventResolutionException()

		if self.to.facing_mode == ZoneFacingMode.STACK and len(self.to) >= 2 and self.to[-1] == cardboard:
			self.spawn_tree(TurnCardboard, face_up=False, target=self.to[-2], frm=self.to)

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
	def frm(self) -> Zone:
		return self._values['frm']

	@frm.setter
	def frm(self, zone: Zone) -> None:
		self._values['frm'] = zone

	@property
	def face_up(self) -> bool:
		return self._values['face_up']

	@face_up.setter
	def face_up(self, face_up: bool) -> None:
		self._values['face_up'] = face_up

	def check(self, **kwargs):
		if self.target.face_up == self.face_up or not self.target in self.frm:
			raise EventCheckException()

	def payload(self, **kwargs):
		self.target.face_up = self.face_up


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

	def check(self, **kwargs):
		if not self.target in self.frm:
			raise EventCheckException()

	def payload(self, **kwargs):
		previous_visibility = {player: self.target.visible(player) for player in self.target.id_map}
		cardboard = self.depend_tree(MoveZoneable) #type: Cardboard
		if self.face_up is not None:
			self.spawn_tree(TurnCardboard)
		else:
			if self.to.facing_mode == ZoneFacingMode.STACK and len(self.to) >= 2 and self.target == self.to[-1]:
				self.spawn_tree(TurnCardboard, target = self.to[-2], face_up = False, frm=self.to)
			elif self.to.facing_mode == ZoneFacingMode.FACE_UP:
				self.spawn_tree(TurnCardboard, face_up=True, frm=self.to)
			elif self.to.facing_mode == ZoneFacingMode.FACE_DOWN:
				self.spawn_tree(TurnCardboard, face_up=False, frm=self.to)
			if self.frm.facing_mode == ZoneFacingMode.STACK and self.frm:
				self.spawn_tree(TurnCardboard, target = self.frm[-1], face_up = True, frm=self.to)
		if self.frm.ordered == False and self.to.ordered == True:
			for player in cardboard.id_map:
				if not cardboard.visible(player):
					cardboard.id_map[player] = None
		elif self.frm.ordered == True and self.to.ordered == False:
			for player in cardboard.id_map:
				if not previous_visibility[player]:
					cardboard.id_map[player] = self._session.id_provider.get_id()
		return cardboard


class RevealCardboard(GameEvent):

	@property
	def target(self) -> Cardboard:
		return self._values['target']

	@target.setter
	def target(self, cardboard: Cardboard) -> None:
		self._values['target'] = cardboard

	@property
	def players(self) -> t.List[Player]:
		return self._values['players']

	@players.setter
	def players(self, players: t.List[Player]) -> None:
		self._values['players'] = players

	def payload(self, **kwargs):
		pass


class RevealCardboards(GameEvent):

	@property
	def players(self) -> t.Optional[t.List[Player]]:
		return self._values['players']

	@players.setter
	def players(self, players: t.Optional[t.List[Player]]) -> None:
		self._values['players'] = players

	@property
	def targets(self) -> t.List[Cardboard]:
		return self._values['targets']

	@targets.setter
	def targets(self, targets: t.List[Cardboard]) -> None:
		self._values['targets'] = targets

	def setup(self, **kwargs):
		self._values.setdefault('players', None)

	def payload(self, **kwargs):
		for cardboard in self.targets:
			for player in (self.players if self.players is not None else self.game.players):
				player.peeking.append(cardboard)
				self.spawn_tree(RevealCardboard, target=cardboard)
				player.peeking.remove(cardboard)


class Discard(GameEvent):

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

	def setup(self, **kwargs):
		self._values.setdefault('frm', self.player.hand)

	def payload(self, **kwargs):
		return self.depend_tree(MoveCardboard, to=self.player.graveyard)


class Destroy(GameEvent):

	@property
	def target(self) -> Cardboard:
		return self._values['target']

	@target.setter
	def target(self, cardboard: Cardboard) -> None:
		self._values['target'] = cardboard

	def payload(self, **kwargs):
		self.depend_tree(MoveCardboard, frm=self.player.battlefield, to=self.player.graveyard)


class CreatePile(GameEvent):

	@property
	def pile_type(self) -> t.Type[Pile]:
		return self._values['pile_type']

	@pile_type.setter
	def pile_type(self, pile_type: t.Type[Pile]) -> None:
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

	def setup(self, **kwargs):
		self._values.setdefault('setup_values', dict())
		self._values.setdefault('in_supply', True)

	def payload(self, **kwargs):
		pile = self.pile_type(self.game, self)
		if self.in_supply:
			self.game.supply_piles[pile.name] = pile
		else:
			self.game.non_supply_piles[pile.name] = pile
		pile.setup(self)


class CreateBuyableEvent(GameEvent):

	@property
	def buyable_event_type(self) -> t.Type[BuyableEvent]:
		return self._values['buyable_event_type']

	@buyable_event_type.setter
	def buyable_event_type(self, event_type: t.Type[BuyableEvent]) -> None:
		self._values['buyable_event_type'] = event_type

	@property
	def setup_values(self) -> t.Dict[str, t.Any]:
		return self._values['setup_values']

	def setup(self, **kwargs):
		self._values.setdefault('setup_values', dict())

	def payload(self, **kwargs):
		event = self.buyable_event_type(self.game, self)
		self.game.buyable_events[event.name] = event
		event.setup(self)


class CreateStartLibrary(GameEvent):

	@property
	def content(self) -> t.List[t.Union[str, t.Type[Card]]]:
		return self._values['content']

	@content.setter
	def content(self, content: t.List[t.Union[str, t.Type[Card]]]):
		self._values['content'] = content

	def payload(self, **kwargs):
		for card in self.content:
			if isinstance(card, str):
				self.spawn_tree(Take, pile=self.game.supply_piles[card])
			else:
				self.spawn_tree(CreateCardboard, to=self.player.graveyard, card_type=card)


class RequireNonSupplyPile(GameEvent):

	@property
	def pile_type(self) -> t.Type[Pile]:
		return self._values['pile_type']

	@pile_type.setter
	def pile_type(self, pile_type: t.Type[Pile]) -> None:
		self._values['pile_type'] = pile_type

	def check(self, **kwargs):
		if self.pile_type in map(type, self.game.non_supply_piles.values()):
			raise EventCheckException()

	def payload(self, **kwargs):
		self.spawn_tree(CreatePile, in_supply=False)


class Setup(GameEvent):

	@property
	def info(self) -> SetupInfo:
		return self._values['info']

	# @property
	# def seed(self) -> t.Optional[t.ByteString]:
	# 	return self._values['seed']
	#
	# @seed.setter
	# def seed(self, value: t.Optional[t.ByteString]):
	# 	self._values['seed'] = value

	@property
	def basic_supply(self) -> t.Dict[str, t.Type[Pile]]:
		return self._values['basic_supply']

	@property
	def all_piles(self) -> t.Dict[str, t.Type[Pile]]:
		return self._values['all_piles']

	@property
	def all_buyable_events(self) -> t.Dict[str, t.Type[BuyableEvent]]:
		return self._values['all_buyable_events']

	def setup(self, **kwargs):
		self._values.setdefault('seed', None)

	def payload(self, **kwargs):
		# if self.seed is not None:
		# 	random.seed(self.seed)
		# else:
		# 	random.seed()

		self.game._replacement_chooser = ChooseReplacement
		self.game._turn_event_type = TakeTurn

		self.game.trash = Zone(
			session = self.game,
			event = self,
			owner = None,
			name='trash',
			facing_mode=ZoneFacingMode.FACE_UP,
			owner_see_face_down=False,
			ordered=True,
		)

		self.game.tokens = Zone(
			session = self.game,
			event = self,
			owner = None,
			name = 'tokens',
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		)

		self.game.turn_order = TurnOrder(
			Player(
				session = self.game,
				event = self,
				interface = self.game.interface,
				id = self.game.id_provider.get_id(),
			)
			for _ in range(self.info.num_players)
		)

		for key, value in self.basic_supply.items():
			self.spawn_tree(CreatePile, pile_type=value)

		for pile_info in self.info.kingdom_info.piles:
			pile_type = self.all_piles.get(pile_info.name)
			if pile_type:
				self.spawn_tree(CreatePile, pile_type=pile_type, setup_values=pile_info.values)

		for buyable_event_info in self.info.kingdom_info.events:
			event_type = self.all_buyable_events.get(buyable_event_info.name)
			if event_type:
				self.spawn_tree(
					CreateBuyableEvent,
					buyable_event_type = event_type,
					setup_values = buyable_event_info.values
				)

		self.game.terminator_piles = ['Province']

		for player in self.game.players:
			self.branch(CreateStartLibrary, player=player, content=['Copper']*7+['Estate']*3)

		for player in self.game.players:
			self.branch(Reshuffle, player=player)

		for player in self.game.players:
			self.branch(DrawHand, player=player)


class ChooseReplacement(GameEvent):

	@property
	def options(self) -> 't.Sequence[Replacement]':
		return self._values['options']

	def payload(self, **kwargs):
		if self.game.turn_order is None:
			return sorted(self.options, key=lambda replacement: replacement.time_stamp)[0]

		for player in self.game.turn_order.ap_nap():
			_options = [
				option
				for option in self.options
				if (
					isinstance(option.source, Cardboard)
					and option.source.cardboard.owner == player
				) or (
					isinstance(option.source, Player)
					and option.source == player
				)
			]
			if _options:
				return player.pick_option(
					options = lambda : _options,
					add_opp_treatment = AdditionalOptionTreatment.IGNORE,
					reason = 'Choose replacement',
				)

		return sorted(self.options, key=lambda replacement: replacement.time_stamp)[0]


class ResolveTriggers(GameEvent):

	def payload(self, **kwargs):
		if self.game.turn_order is None:
			while self.game.trigger_queue:
				self.game.trigger_queue.pop().resolve(self)
			return

		for player in self.game.turn_order.ap_nap():
			_options = [
				option
				for option in self.game.trigger_queue
				if isinstance(option.source, Cardboard)
				and option.source.cardboard.owner == player
			]

			while _options:
				picked = self.player.pick_option(
					options = lambda : _options,
					add_opp_treatment = AdditionalOptionTreatment.IGNORE,
					reason = 'Choose Trigger',
				)
				_options.remove(picked)
				self.game.trigger_queue.remove(picked)
				picked.resolve(self)

		while self.game.trigger_queue:
			self.game.trigger_queue.pop().resolve(self)

		self.game.trigger_queue[:] = []


class Upkeep(GameEvent):

	@property
	def turn(self) -> Turn:
		return self._values['turn']

	@turn.setter
	def turn(self, turn: Turn) -> None:
		self._values['turn'] = turn

	def payload(self, **kwargs):
		self.spawn_tree(SetActions, player=self.player, amount=1)
		self.spawn_tree(SetBuys, player=self.player, amount=1)


class ActionPhase(GameEvent):

	@property
	def turn(self) -> Turn:
		return self._values['turn']

	@turn.setter
	def turn(self, turn: Turn) -> None:
		self._values['turn'] = turn

	def payload(self, **kwargs):
		finished = 'End action phase'
		picked = None

		while picked != finished and (self.player.actions > 0 or self.player.has_additional_options()):
			picked = self.player.pick_option(
				lambda : [
					cardboard
					for cardboard in
					self.player.hand
					if CardType.ACTION in cardboard.type_line
				] + [finished],
				add_opp_treatment = AdditionalOptionTreatment.MERGE,
				reason = 'Select action',
			)
			if isinstance(picked, Cardboard):
				self.spawn_tree(AddAction, amount=-1)
				self.spawn_tree(CastCardboard, target=picked)


class TreasurePhase(GameEvent):

	@property
	def turn(self) -> Turn:
		return self._values['turn']

	@turn.setter
	def turn(self, turn: Turn) -> None:
		self._values['turn'] = turn

	def payload(self, **kwargs):
		finished = 'End treasure phase'
		picked = None

		while picked != finished:
			picked = self.player.pick_option(
				lambda : [
					cardboard
					for cardboard in
					self.player.hand
					if CardType.TREASURE in cardboard.type_line
				] + [finished],
				add_opp_treatment = AdditionalOptionTreatment.MERGE,
				reason = 'Select Treasure',
			)
			if isinstance(picked, Cardboard):
				self.spawn_tree(CastCardboard, target=picked)


class BuyPhase(GameEvent):

	@property
	def turn(self) -> Turn:
		return self._values['turn']

	@turn.setter
	def turn(self, turn: Turn) -> None:
		self._values['turn'] = turn

	def payload(self, **kwargs):
		finished = 'End buy phase'
		picked = None

		while picked != finished and (self.player.buys > 0 or self.player.has_additional_options()):
			picked = self.player.pick_option(
				lambda :
					self.game.piles_up_to(self.player.currency)
					+ [
						event
						for event in
						self.game.buyable_events.values()
						if event.price.value <= self.player.currency
					]
					+ [finished],
				reason = 'Select buy',
			)
			if isinstance(picked, Pile):
				self.spawn_tree(AddBuy, amount=-1)
				self.spawn_tree(BuyCardboard, pile=picked)
			elif isinstance(picked, BuyableEvent):
				self.spawn_tree(AddBuy, amount=-1)
				self.spawn_tree(BuyBuyableEvent, event=picked)


class NightPhase(GameEvent):

	@property
	def turn(self) -> Turn:
		return self._values['turn']

	@turn.setter
	def turn(self, turn: Turn) -> None:
		self._values['turn'] = turn

	def payload(self, **kwargs):
		finished = 'End night phase'
		picked = None

		while picked != finished:
			picked = self.player.pick_option(
				lambda : [
					cardboard
					for cardboard in
					self.player.hand
					if CardType.NIGHT in cardboard.type_line
				] + [finished],
				add_opp_treatment = AdditionalOptionTreatment.MERGE,
				reason = 'Select night',
			)
			if isinstance(picked, Cardboard):
				self.spawn_tree(CastCardboard, target=picked)


class CleanUpPhase(GameEvent):

	@property
	def turn(self) -> Turn:
		return self._values['turn']

	@turn.setter
	def turn(self, turn: Turn) -> None:
		self._values['turn'] = turn

	def payload(self, **kwargs):
		_player = self.player
		self.branch(SetCurrency, player= _player, amount=CurrencyValue(0, 0, 0))
		self.branch(SetBuys, player= _player, amount=0)
		self.branch(SetActions, player= _player, amount=0)
		for cardboard in tuple(self.player.hand):
			self.spawn_tree(Discard, target=cardboard)
		for cardboard in tuple(self.player.battlefield):
			self.spawn_tree(Destroy, target=cardboard)
		self.branch(DrawHand, player=_player)


class TakeTurn(GameEvent):

	@property
	def turn(self) -> Turn:
		return self._values['turn']

	@turn.setter
	def turn(self, turn: Turn) -> None:
		self._values['turn'] = turn

	def setup(self, **kwargs):
		self._values.setdefault('player', self.turn.player)

	def payload(self, **kwargs):
		self.spawn_tree(Upkeep)
		self.spawn_tree(ResolveTriggers)

		self.spawn_tree(ActionPhase)
		self.spawn_tree(ResolveTriggers)

		self.spawn_tree(TreasurePhase)
		self.spawn_tree(ResolveTriggers)

		self.spawn_tree(BuyPhase)
		self.spawn_tree(ResolveTriggers)

		self.spawn_tree(NightPhase)
		self.spawn_tree(ResolveTriggers)

		self.spawn_tree(CleanUpPhase)
		self.spawn_tree(ResolveTriggers)


class Attack(GameEvent):

	@property
	def victim(self) -> Player:
		return self._values['victim']

	@victim.setter
	def victim(self, victim: Player) -> None:
		self._values['victim'] = victim

	@property
	def attacker(self) -> Cardboard:
		return self._values['attacker']

	@attacker.setter
	def attacker(self, attacker: Cardboard) -> None:
		self._values['attacker'] = attacker

	def payload(self, **kwargs):
		self.attacker.attack(self)


class GameFinished(GameEvent):

	@property
	def winners(self) -> t.Collection[Player]:
		return self._values['winners']

	@winners.setter
	def winners(self, player: t.Collection[Player]) -> None:
		self._values['winners'] = player

	@property
	def points(self) -> t.Dict[Player, int]:
		return self._values['points']

	@points.setter
	def points(self, points: t.Dict[Player, int]) -> None:
		self._values['points'] = points

	def payload(self, **kwargs):
		pass


class EndGame(GameEvent):

	def payload(self, **kwargs):
		points = {
			player: self.game.vp(player)
			for player in
			self.game.players
		}
		winning_points = max(points.values())
		winners = [
			player
			for player in
			points if
			points[player] == winning_points
		]
		self.branch(GameFinished, points=points, winners=winners)


class Play(GameEvent):

	def payload(self, **kwargs):
		while not self.game.check_finished():
			self.branch(TakeTurn, turn=self.game.turn_order.next())
		self.spawn_tree(EndGame)


class ShuffleZone(GameEvent):

	@property
	def to(self) -> Zone:
		return self._values['to']

	@to.setter
	def to(self, zone: Zone) -> None:
		self._values['to'] = zone

	@property
	def index(self) -> t.Optional[int]:
		return self._values['index']

	@index.setter
	def index(self, index: t.Optional[int]):
		self._values['index'] = index

	def setup(self, **kwargs):
		self._values.setdefault('player', None)
		self._values.setdefault('index', None)
		if self.player is not None:
			self._values.setdefault('to', self.player.library)

	def check(self, **kwargs):
		if not self.to.ordered:
			raise EventCheckException()

	def payload(self, **kwargs):
		if self.to.facing_mode == ZoneFacingMode.STACK:
			for cardboard in self.to[:self.index]:
				self.spawn_tree(TurnCardboard, target=cardboard, face_up=False)
		for cardboard in self.to[:self.index]:
			for observer in cardboard.id_map:
				if not cardboard.visible(observer):
					cardboard.id_map[observer] = self.game.id_provider.get_id()
		self.to.shuffle(self.index)
		if self.to.facing_mode == ZoneFacingMode.STACK and self.index is None:
			self.spawn_tree(TurnCardboard, target=self.to[-1], face_up=True)


class Reshuffle(GameEvent):

	def payload(self, **kwargs):
		if self.player.library:
			index = len(self.player.graveyard)
			for cardboard in tuple(self.player.graveyard):
				self.spawn_tree(
					MoveCardboard,
					frm=self.player.graveyard,
					to=self.player.library,
					target=cardboard,
					index = 0,
				)
			self.spawn_tree(ShuffleZone, index=index)
		else:
			for cardboard in tuple(self.player.graveyard):
				self.spawn_tree(
					MoveCardboard,
					frm = self.player.graveyard,
					to = self.player.library,
					target = cardboard,
				)
			self.spawn_tree(ShuffleZone)


class RequestCardboards(GameEvent):

	@property
	def amount(self) -> int:
		return self._values['amount']

	@amount.setter
	def amount(self, value: int) -> None:
		self._values['amount'] = value

	def payload(self, **kwargs):
		if len(self.player.library) < self.amount:
			self.spawn_tree(Reshuffle)
		return self.player.library[-self.amount:]


class DrawCardboard(GameEvent):

	def payload(self, **kwargs):
		if not self.player.library:
			self.spawn_tree(Reshuffle)
		if not self.player.library:
			raise EventResolutionException()
		return self.depend_tree(
			MoveCardboard,
			frm = self.player.library,
			to = self.player.hand,
			target = self.player.library[-1],
		)


class DrawCardboards(GameEvent):

	@property
	def amount(self) -> int:
		return self._values['amount']

	@amount.setter
	def amount(self, value: int) -> None:
		self._values['amount'] = value

	def payload(self, **kwargs):
		cardboards = []
		for _ in range(self.amount):
			cardboard = self.spawn_tree(DrawCardboard)
			if cardboard is None:
				break
			cardboards.append(cardboard)
		return cardboards


class DrawHand(GameEvent):

	@property
	def amount(self) -> int:
		return self._values['amount']

	@amount.setter
	def amount(self, value: int) -> None:
		self._values['amount'] = value

	def setup(self, **kwargs):
		self._values.setdefault('amount', 5)

	def payload(self, **kwargs):
		return self.depend_tree(DrawCardboards)


class Gain(GameEvent):

	@property
	def target(self) -> Cardboard:
		return self._values['target']

	@target.setter
	def target(self, cardboard: Cardboard) -> None:
		self._values['target'] = cardboard

	@property
	def pile(self) -> Pile:
		return self._values['pile']

	@pile.setter
	def pile(self, pile: Pile) -> None:
		self._values['pile'] = pile

	@property
	def to(self) -> Zone:
		return self._values['to']

	@to.setter
	def to(self, zone: Zone) -> None:
		self._values['to'] = zone

	def setup(self, **kwargs):
		self._values.setdefault('to', self.player.graveyard)

	def check(self, **kwargs):
		if not self.pile.cardboards:
			raise EventCheckException()
		self._values['target'] = self.pile.cardboards[-1]

	def payload(self, **kwargs):
		return self.depend_tree(
			MoveCardboard,
			frm = self.pile.cardboards,
			to = self.to,
		)


class Take(Gain):
	pass


class BuyCardboard(GameEvent):

	@property
	def pile(self) -> Pile:
		return self._values['pile']

	@pile.setter
	def pile(self, pile: Pile) -> None:
		self._values['pile'] = pile

	@property
	def to(self) -> Zone:
		return self._values['to']

	@to.setter
	def to(self, zone: Zone) -> None:
		self._values['to'] = zone

	def setup(self, **kwargs):
		self._values.setdefault('to', self.player.graveyard)

	def check(self, **kwargs):
		if not self.pile.cardboards:
			raise EventCheckException()

	def payload(self, **kwargs):
		self.spawn_tree(AddCurrency, amount=-self.pile.cardboards[-1].price.value)
		return self.spawn_tree(Gain)


class Trash(GameEvent):

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

	def payload(self, **kwargs):
		return self.depend_tree(MoveCardboard, to=self.game.trash)


class Return(GameEvent):

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

	def check(self, **kwargs):
		if self.target.origin_zone is None:
			raise EventCheckException

	def payload(self, **kwargs):
		return self.spawn_tree(MoveCardboard, to=self.target.origin_zone)


class BuyBuyableEvent(GameEvent):

	@property
	def event(self) -> BuyableEvent:
		return self._values['event']

	@event.setter
	def event(self, event: BuyableEvent) -> None:
		self._values['event'] = event

	def payload(self, **kwargs):
		self.spawn_tree(AddCurrency, amount=-self.event.price.value)
		self.event.on_buy(self)


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


class SetCurrency(GameEvent):

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
		self.player.currency = self.amount


class ResolveCardboard(GameEvent):

	@property
	def target(self) -> Cardboard:
		return self._values['target']

	@target.setter
	def target(self, cardboard: Cardboard) -> None:
		self._values['cardboard'] = cardboard

	def payload(self, **kwargs):
		self.target.on_play(self)
		return self.target


class CastCardboard(GameEvent):

	@property
	def frm(self) -> Zone:
		return self._values['frm']

	@frm.setter
	def frm(self, zone: Zone) -> None:
		self._values['frm'] = zone

	@property
	def target(self) -> Cardboard:
		return self._values['target']

	@target.setter
	def target(self, cardboard: Cardboard) -> None:
		self._values['cardboard'] = cardboard

	@property
	def caster(self) -> t.Optional[Cardboard]:
		return self._values['caster']

	@caster.setter
	def caster(self, caster: t.Optional[Cardboard]) -> None:
		self._values[caster] = caster

	def setup(self, **kwargs):
		self._values.setdefault('frm', self.player.hand)
		self._values.setdefault('caster', None)

	def payload(self, **kwargs):
		self.depend_tree(MoveCardboard, to=self.player.battlefield)
		self.target.attachments[:] = []
		if self.caster:
			self.caster.attachments.append(self.target)
		return self.spawn_tree(ResolveCardboard)


class AddAction(GameEvent):

	@property
	def amount(self) -> int:
		return self._values['amount']

	@amount.setter
	def amount(self, amount: int) -> None:
		self._values['amount'] = amount

	def payload(self, **kwargs):
		self.player.actions += self.amount


class SetActions(GameEvent):

	@property
	def amount(self) -> int:
		return self._values['amount']

	@amount.setter
	def amount(self, amount: int) -> None:
		self._values['amount'] = amount

	def payload(self, **kwargs):
		self.player.actions = self.amount


class AddBuy(GameEvent):

	@property
	def amount(self) -> int:
		return self._values['amount']

	@amount.setter
	def amount(self, amount: int) -> None:
		self._values['amount'] = amount

	def payload(self, **kwargs):
		self.player.buys += self.amount


class SetBuys(GameEvent):

	@property
	def amount(self) -> int:
		return self._values['amount']

	@amount.setter
	def amount(self, amount: int) -> None:
		self._values['amount'] = amount

	def payload(self, **kwargs):
		self.player.buys = self.amount
