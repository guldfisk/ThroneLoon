import typing as t

from eventtree.replaceevent import Event

from eventtree.replaceevent import (
	EventSession, DelayedReplacement, Reaction, Replacement, PostReaction, Response, PreResponse
)

from throneloon.game import gameevents as ge

from throneloon.models.templates.cards import Treasure, Action, Victory, Duration, Night
from throneloon.game.artifacts.cards import Cardboard, Card
from throneloon.game.values.currency import Value, Price, CurrencyValue
from throneloon.game.values.cardtypes import CardType, TypeLine
from throneloon.game.artifacts.players import AdditionalOptionTreatment
from throneloon.game.artifacts.kingdomcomponents import Pile


class Copper(Treasure):
	name = 'Copper'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._value = Value(session, self, 1)
		self._price = Price(session, self, 0)


class Silver(Treasure):
	name = 'Silver'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._value = Value(session, self, 2)
		self._price = Price(session, self, 3)


class Gold(Treasure):
	name = 'Gold'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._value = Value(session, self, 3)
		self._price = Price(session, self, 6)


class Estate(Victory):
	name = 'Estate'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._vp_value = 1
		self._price = Price(session, self, 2)


class Duchy(Victory):
	name = 'Duchy'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._vp_value = 3
		self._price = Price(session, self, 5)


class Province(Victory):
	name = 'Province'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._vp_value = 6
		self._price = Price(session, self, 8)


class Curse(Card):
	name = 'Curse'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._type_line += TypeLine((CardType.CURSE,))
		self._price = Price(session, self, 0)

	def vp_value(self) -> int:
		return -1


class Village(Action):
	name = 'Village'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 3)

	def on_play(self, event: ge.ResolveCardboard):
		event.spawn_tree(ge.DrawCardboards, amount=1)
		event.spawn_tree(ge.AddAction, amount=2)


class Cellar(Action):
	name = 'Cellar'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 2)

	def on_play(self, event: ge.ResolveCardboard):
		event.spawn_tree(ge.AddAction, amount=1)
		cardboards = event.player.pick_options(
			options = event.player.hand,
			minimum = 0,
			reason = 'Choose discard',
		)
		for cardboard in cardboards:
			event.spawn_tree(ge.Discard, target=cardboard)
		event.spawn_tree(ge.DrawCardboards, amount=len(cardboards))


class Chapel(Action):
	name = 'Chapel'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 2)

	def on_play(self, event: ge.ResolveCardboard):
		for cardboard in event.player.pick_options(
			options = event.player.hand,
			minimum = 0,
			maximum = 4,
			reason = 'Choose trash',
		):
			event.spawn_tree(ge.Trash, target=cardboard, frm=event.player.hand)


class Moat(Action):
	name = 'Moat'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 2)
		self._type_line += CardType.REACTION

		self._bubbeling = [] #type: t.List[Cardboard]

		self.create_condition(
			Reaction,
			parent = event,
			trigger = 'ResolveCardboard',
			condition = lambda react_event: (
				self.cardboard.zone.name == 'hand'
				and CardType.ATTACK in react_event.target.type_line
				and react_event.player != self.cardboard.owner
			),
			react = lambda react_event: self._bubble(react_event.target, react_event),
		)

	def _bubble(self, attacker: Cardboard, event: Event) -> None:
		event.spawn_tree(ge.RevealCardboards, targets=[self.cardboard])
		if not attacker in self._bubbeling:
			self._bubbeling.append(attacker)
			self.create_condition(
				DelayedReplacement,
				parent = event,
				trigger = 'Attack',
				condition = lambda attack_event: (
					attack_event.victim == self.cardboard.owner
					and attack_event.attacker == attacker
				),
				replace = lambda : self._bubbeling.remove(attacker),
			)

	def on_play(self, event: ge.ResolveCardboard):
		event.spawn_tree(ge.DrawCardboards, amount=2)



class Militia(Action):
	name = 'Militia'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 4)
		self._type_line += CardType.ATTACK

	def on_play(self, event: ge.ResolveCardboard):
		event.spawn_tree(ge.AddCurrency, amount=CurrencyValue(2))
		for player in event.game.turn_order.other_players(event.player):
			event.spawn_tree(ge.Attack, attacker=self.cardboard, victim=player)

	def attack(self, event: ge.Attack):
		amount = len(event.victim.hand) - 3
		for cardboard in event.victim.pick_options(
			options = event.victim.hand,
			minimum = amount,
			maximum = amount,
			reason = 'Choose discard',
		):
			event.branch(ge.Discard, target=cardboard, player=event.victim)


class ThroneRoom(Action):
	name = 'Throne Room'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 4)

		self.create_condition(
			Replacement,
			parent = event,
			trigger = 'Destroy',
			condition = lambda destroy_event: (
				destroy_event.target==self.cardboard
				and any(
					attachment.need_tre(destroy_event)
					for attachment in
					self.cardboard.attachments
				)
			),
		)

	def on_play(self, event: ge.ResolveCardboard):
		cardboard = event.player.pick_option(
			options = lambda : (
				cardboard
				for cardboard in event.player.hand
				if CardType.ACTION in cardboard.type_line
			),
			optional = True,
			reason = 'Choose action',
		)
		if cardboard:
			if event.spawn_tree(ge.CastCardboard, target=cardboard, caster=self.cardboard):
				event.player.resolve_add_ops()
				event.spawn_tree(ge.ResolveCardboard, target=cardboard)

	def need_tre(self, event: Event) -> bool:
		return len(
			[
				cardboard
				for cardboard in
				self.cardboard.attachments
				if cardboard.need_tre(event)
			]
		) > 1


class Watchtower(Action):
	name = 'Watchtower'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 3)
		self._type_line += CardType.REACTION

		self.create_condition(
			PostReaction,
			parent = event,
			trigger = 'Gain',
			condition = lambda gain_event: (
				self.cardboard.zone.name == 'hand'
				and self.cardboard.owner == gain_event.player
			),
			react = self._react,
		)

	def _react(self, event: ge.Gain):
		event.spawn_tree(ge.RevealCardboards, targets=[self])
		if event.player.pick_option(
			('Trash', 'Top deck'),
			reason = 'Choose gained card location'
		) == 'Trash':
			event.spawn_tree(ge.MoveCardboard, frm=event.to, to=event.game.trash, )
		else:
			event.spawn_tree(ge.MoveCardboard, frm=event.to, to=event.player.library)

	def on_play(self, event: ge.ResolveCardboard):
		while len(event.player.hand) < 6:
			if event.spawn_tree(ge.DrawCardboards, amount=1) is None:
				break


class Wharf(Duration):
	name = 'Wharf'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 5)
		self._type_line += CardType.ACTION

	def on_play(self, event: ge.ResolveCardboard):
		super().on_play(event)
		event.spawn_tree(ge.DrawCardboards, amount=2)
		event.spawn_tree(ge.AddBuy, amount=1)

	def next_turn(self, event: ge.Upkeep):
		event.spawn_tree(ge.DrawCardboards, amount=2)
		event.spawn_tree(ge.AddBuy, amount=1)



class Trader(Action):
	name = 'Trader'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 4)
		self._type_line += CardType.REACTION

		self.create_condition(
			Replacement,
			parent = event,
			trigger = 'Gain',
			condition = lambda gain_event: (
				self.cardboard.zone.name == 'hand'
				and self.cardboard.owner == gain_event.player
			),
			replace = self._replace,
		)

	def _replace(self, event: ge.Gain):
		if event.player.pick_option(('yes', 'no'), reason='Trader react') == 'yes':
			event.replace(ge.RevealCardboards, targets=[self])
			event.replace_clone(pile=event.game.supply_piles['Silver'])
		else:
			event.resolve()

	def on_play(self, event: ge.ResolveCardboard):
		cardboard = event.player.pick_option(
			options = event.player.hand,
			reason = 'Choose trash',
		)
		if not cardboard:
			return
		event.spawn_tree(ge.Trash, target=cardboard, frm=event.player.hand)
		for _ in range(cardboard.price.value.coin_value):
			event.spawn_tree(ge.Gain, pile=event.game.supply_piles['Silver'])


class SecretChamber(Action):
	name = 'Secret Chamber'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 2)
		self._type_line += CardType.REACTION

		self.create_condition(
			Reaction,
			parent = event,
			trigger = 'ResolveCardboard',
			condition = lambda resolve_event: (
				self.cardboard.zone.name == 'hand'
				and self.cardboard.owner != resolve_event.player
				and CardType.ATTACK in resolve_event.target.type_line
			),
			react = self._react,
		)

	def _react(self, event: ge.ResolveCardboard):
		_player = self.cardboard.owner
		event.branch(ge.RevealCardboards, targets=[self.cardboard], player=_player)
		event.branch(ge.DrawCardboards, amount=2, player=_player)
		for cardboard in _player.pick_options(
			options = _player.hand,
			minimum = 2,
			maximum = 2,
			reason = 'Choose put back',
		):
			event.spawn_tree(
				ge.MoveCardboard,
				frm = _player.hand,
				to = _player.library,
				target = cardboard,
			)

	def on_play(self, event: ge.ResolveCardboard):
		cardboards = event.player.pick_options(
			options = event.player.hand,
			minimum = 0,
			maximum = None,
			reason = 'Choose discard',
		)
		for cardboard in cardboards:
			event.spawn_tree(ge.Discard, target=cardboard)
		event.spawn_tree(
			ge.AddCurrency,
			amount = CurrencyValue(
				len(cardboards)
			)
		)


class Hamlet(Action):
	name = 'Hamlet'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 2)

	@staticmethod
	def _action(event: ge.ResolveCardboard):
		cardboard = event.player.pick_option(
			options = event.player.hand,
			add_opp_treatment = AdditionalOptionTreatment.IGNORE,
			reason = 'Choose discard',
		)
		if cardboard:
			if event.spawn_tree(ge.Discard, target=cardboard):
				event.spawn_tree(ge.AddAction, amount=1)

	@staticmethod
	def _buy(event: ge.ResolveCardboard):
		cardboard = event.player.pick_option(
			options = event.player.hand,
			add_opp_treatment=AdditionalOptionTreatment.IGNORE,
			reason = 'Choose discard',
		)
		if cardboard:
			if event.spawn_tree(ge.Discard, target=cardboard):
				event.spawn_tree(ge.AddBuy, amount=1)

	def on_play(self, event: ge.ResolveCardboard):
		event.spawn_tree(ge.DrawCardboards, amount=1)
		event.spawn_tree(ge.AddAction, amount=1)

		event.player.register_additional_option(
			option = 'Discard for action',
			action = lambda : self._action(event),
		)
		event.player.register_additional_option(
			option = 'Discard for buy',
			action = lambda : self._buy(event),
		)


class ZombieApprentice(Action):
	name = 'Zombie Apprentice'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 3)
		self._type_line += CardType.ZOMBIE

	def on_play(self, event: ge.ResolveCardboard):
		cardboard = event.player.pick_option(
			options = event.player.hand,
			optional = True,
			reason = 'Choose trash',
		)
		if cardboard and event.spawn_tree(ge.Trash, target=cardboard, frm=event.player.hand):
			event.spawn_tree(ge.DrawCardboards, amount=3)
			event.spawn_tree(ge.AddAction, amount=1)


class ZombieMason(Action):
	name = 'Zombie Mason'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 3)
		self._type_line += CardType.ZOMBIE

	def on_play(self, event: ge.ResolveCardboard):
		cardboards = event.spawn_tree(ge.RequestCardboards, amount=1)
		if cardboards:
			_cardboard = cardboards[0]
			event.spawn_tree(ge.Trash, target=_cardboard, frm=event.player.library)
			pile = event.player.pick_option(
				options = lambda : event.game.piles_cheaper_than(_cardboard.price.value),
				optional = True,
				reason = 'Choose gain',
			)
			if pile:
				event.spawn_tree(ge.Gain, pile=pile)


class ZombieSpy(Action):
	name = 'Zombie Spy'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 3)
		self._type_line += CardType.ZOMBIE

	def on_play(self, event: ge.ResolveCardboard):
		event.spawn_tree(ge.DrawCardboards, amount=1)
		event.spawn_tree(ge.AddAction, amount=1)
		cardboards = event.spawn_tree(ge.RequestCardboards, amount=1)
		if cardboards:
			_cardboard = cardboards[0]
			event.spawn_tree(ge.RevealCardboards, targets=[_cardboard], players=[event.player])
			if event.player.pick_option(
				options = ('Discard', 'Stay'),
				reason = 'Choose card location',
			) == 'Discard':
				event.spawn_tree(ge.Discard, target=_cardboard, frm=event.player.library)


class Necromancer(Action):
	name = 'Necromancer'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 4)

	def on_play(self, event: ge.ResolveCardboard):
		cardboard = event.player.pick_option(
			options = lambda : (
				_cardboard
				for _cardboard in event.game.trash
				if _cardboard.face_up
			   	and CardType.DURATION not in _cardboard.type_line
			)
		)
		if cardboard:
			event.spawn_tree(ge.TurnCardboard, target=cardboard, face_up=False, frm=event.game.trash)
			event.spawn_tree(ge.ResolveCardboard, target=cardboard)
			self.create_condition(
				Response,
				parent = event,
				trigger = 'CleanUpPhase',
				resolve = lambda _event:
					_event.spawn_tree(ge.TurnCardboard, target=cardboard, face_up=True, frm=event.game.trash)
			)


class Imp(Action):
	name = 'Imp'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 2)

	def on_play(self, event: ge.ResolveCardboard):
		event.spawn_tree(ge.DrawCardboards, amount=2)
		action = event.player.pick_option(
			options = lambda :
				[
					cardboard
					for cardboard in event.player.hand
					if CardType.ACTION in cardboard.type_line
					and cardboard.name not in set(
						cardboard.name
						for cardboard in
						event.player.battlefield
					)
				],
			optional = True,
			reason = 'Choose gain',
		)
		if action:
			event.spawn_tree(ge.CastCardboard, target=action)


class DevilsWorkshop(Night):
	name = "Devil's Workshop"

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 4)

	def on_play(self, event: ge.ResolveCardboard):
		amount_gained = len(
			[
				_event
				for _event in event.game.turn_log()
				if isinstance(_event, ge.Gain)
				and _event.player == event.player
			]
		)
		print('devils', amount_gained, list(event.game.turn_log()))
		if amount_gained == 0:
			event.spawn_tree(ge.Gain, pile=event.game.supply_piles['Gold'])
		elif amount_gained == 1:
			pile = event.player.pick_option(
				options = lambda : event.game.piles_up_to(CurrencyValue(4)),
				reason = 'Choose gain',
			)
			if pile:
				event.spawn_tree(ge.Gain, pile=pile)
		else:
			event.spawn_tree(ge.Gain, pile=event.game.non_supply_piles['Imp'])


class Wish(Action):
	name = 'Wish'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 0)

	def on_play(self, event: ge.ResolveCardboard):
		event.spawn_tree(ge.AddAction, amount=1)
		if not event.spawn_tree(ge.Return, target=self.cardboard, frm=event.player.battlefield):
			return
		pile = event.player.pick_option(
			options = lambda :
				event.game.piles_up_to(CurrencyValue(6)),
			reason = 'Choose gain',
		)
		if pile:
			event.spawn_tree(ge.Gain, pile=pile, to=event.player.hand)


class MagicLamp(Treasure):
	name = 'Magic Lamp'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 0)
		self._value = Value(session, self, 1)

	def on_play(self, event: ge.ResolveCardboard):
		super().on_play(event)
		names = [cardboard.name for cardboard in event.player.battlefield]
		if len([name for name in names if names.count(name)==1]) >= 6:
			if event.spawn_tree(ge.Trash, target=self.cardboard, frm=event.player.battlefield):
				pile = event.game.non_supply_piles['Wish']
				for _ in range(3):
					event.spawn_tree(ge.Gain, pile=pile)


class SecretCave(Duration):
	name = 'Secret Cave'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 3)
		self._type_line += CardType.ACTION

	def on_play(self, event: ge.ResolveCardboard):
		if self._played_on != event.game.turn_order.current_turn():
			self._played_on = None
		event.spawn_tree(ge.DrawCardboards, amount=1)
		event.spawn_tree(ge.AddAction, amount=1)
		event.player.register_additional_option(
			option = self.cardboard,
			action = lambda : self._discard(event),
		)

	def _discard(self, event: ge.ResolveCardboard):
		cardboards = event.player.pick_options(
			options = event.player.hand,
			minimum = 3,
			maximum = 3,
			reason = 'Choose discard',
		)
		if len(
			[
				_cardboard
				for _cardboard in
				(event.spawn_tree(ge.Discard, target=cardboard) for cardboard in cardboards)
				if _cardboard is not None
			]
		) >= 3:
			super().on_play(event)

	def next_turn(self, event: ge.Upkeep):
		event.spawn_tree(ge.AddCurrency, amount=CurrencyValue(3))


class BandOfMisfits(Action):
	name = 'Band of Misfits'

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._price = Price(session, self, 5)

		self.create_condition(
			PreResponse,
			parent = event,
			trigger = 'CastCardboard',
			condition = lambda _event: _event.target == self.cardboard,
			resolve = self._resolve_cast,
		)

	def _resolve_cast(self, event: ge.CastCardboard):
		pile = event.player.pick_option(
			options = lambda :
				(
					pile
					for pile in event.game.piles_cheaper_than(self.price.value)
					if pile.top_cardboard
					and CardType.ACTION in pile.top_cardboard.type_line
				)
			,
			reason = 'Choose imitate',
		) #type: Pile
		if pile:
			self.disconnect(event)
			self.cardboard.card = pile.top_cardboard.printed_card_type(event.game, self.cardboard, event)
			self.cardboard.create_condition(
				PreResponse,
				parent = event,
				trigger = 'MoveCardboard',
				condition = lambda _event: (
					_event.target == self.cardboard
					and _event.frm == event.player.battlefield
					and _event.to != event.player.battlefield
				),
				resolve = self._un_transform,
			)

	def _un_transform(self, event: ge.MoveCardboard):
		self.cardboard.card.disconnect(event)
		self.cardboard.card = self.cardboard.printed_card_type(event.game, self.cardboard, event)