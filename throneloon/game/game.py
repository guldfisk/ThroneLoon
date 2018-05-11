import typing as t

from eventtree.replaceevent import EventSession, Event, Reaction, Replacement

from throneloon.game.artifacts.kingdomcomponents import Pile, BuyableEvent, Landmark
from throneloon.game.artifacts.mats import Mat
from throneloon.game.artifacts.players import Player, AdditionalOptionTreatment
from throneloon.game.artifacts.turns import TurnOrder, Turn
from throneloon.game.artifacts.zones import Zone, ZoneFacingMode
from throneloon.game.artifacts.victory import VictoryValuable
from throneloon.game.artifacts.cards import Cardboard
from throneloon.game.artifacts.artifact import IdSession
from throneloon.game.artifacts.tokens import Token
from throneloon.game.values.currency import CurrencyValue
from throneloon.game.idprovide import IdProvider, IdProviderInterface
from throneloon.io.interface import IOInterface


class Game(IdSession):

	def __init__(self, interface: IOInterface, id_provider: IdProviderInterface):
		super().__init__()

		self._interface = interface #type: IOInterface

		self.id_provider = id_provider #type: IdProviderInterface

		self.turn_order = None #type: TurnOrder

		self._supply_piles = {} #type: t.Dict[str, Pile]
		self._non_supply_piles = {} #type: t.Dict[str, Pile]
		self._buyable_events = {} #type: t.Dict[str, BuyableEvent]
		self.landmarks = {} #type: t.Dict[str, Landmark]

		self.trash = None #type: Zone[Cardboard]

		self.terminator_piles = [] #type: t.List[str]

		self._mats = {} #type: t.Dict[str, Mat]
		self.tokens = None #type: Zone[Token]

		self._turn_event_type = None #type: t.Type[Event]

		# self._boons = Zone(self, None, True, False, False)
		# self._hexes = Zone(self, None, True, False, False)

		self._event_counter = 0 #type: int

	@property
	def interface(self) -> IOInterface:
		return self._interface

	@property
	def players(self) -> t.Sequence[Player]:
		return self.turn_order.players

	@property
	def supply_piles(self) -> t.Dict[str, Pile]:
		return self._supply_piles

	@property
	def non_supply_piles(self) -> t.Dict[str, Pile]:
		return self._non_supply_piles

	@property
	def buyable_events(self) -> t.Dict[str, BuyableEvent]:
		return self._buyable_events

	@property
	def buyables(self) -> t.Dict[str, t.Union[Pile, BuyableEvent]]:
		d = {}
		d.update(self._supply_piles)
		d.update(self._buyable_events)
		return d

	def turn_log(self) -> t.Iterable[Event]:
		for event in reversed(self._event_stack):
			if isinstance(event, self._turn_event_type):
				return
			yield event

	def piles_up_to(self, currency_value: CurrencyValue) -> t.List[Pile]:
		return [
			pile
			for pile in
			self.supply_piles.values()
			if pile.cardboards and pile.cardboards[-1].price.value <= currency_value
		]

	def piles_cheaper_than(self, currency_value: CurrencyValue) -> t.List[Pile]:
		return [
			pile
			for pile in
			self.supply_piles.values()
			if pile.cardboards and pile.cardboards[-1].price.value < currency_value
		]

	def vp(self, player: Player):
		return sum(
			zoneable.vp_value
			for zoneable in
			player.zoneables
			if isinstance(zoneable, VictoryValuable)
		) + sum(
			landmark.vp_value(player)
			for landmark in
			self.landmarks.values()
		)

	def log_event(self, event: Event) -> None:
		self._event_stack.append(event)
		if self.turn_order:
			for player in self.players:
				self._interface.notify_event(event, player, True)

	def event_finished(self, event: 'Event') -> None:
		if self.turn_order:
			for player in self.players:
				self._interface.notify_event(event, player, False)

	def resolve_reactions(self, event: Event, post: bool):
		if not self.turn_order:
			return
		players = self.turn_order.ap_nap()
		player = next(players)
		while True:
			reactions = self.dispatcher.send(
				signal = ('_post_react_' if post else '_react_')+event.__class__.__name__,
				source=event,
			) #type: t.List[Reaction]
			if not reactions:
				break
			reaction_map = {
				reaction.source: reaction
				for connected, reaction in reactions
				if (
					reaction.source.cardboard.owner
					if reaction.source.cardboard.owner is not None else
					self.turn_order.active_player
				) == player
			} #type: t.Dict[Cardboard, Reaction]

			if not reaction_map:
				try:
					player = next(players)
					continue
				except StopIteration:
					break

			done_reacting = 'Done reacting'

			reaction = player.pick_option(
				options = list(reaction_map.keys()) + [done_reacting],
				add_opp_treatment = AdditionalOptionTreatment.IGNORE,
				reason = 'Select reaction',
			)

			if reaction == done_reacting:
				try:
					player = next(players)
					continue
				except StopIteration:
					break
			else:
				reaction_map[reaction].react(event)

	def check_finished(self) -> bool:
		empty_piles = 0
		for key, value in self._supply_piles.items():
			if not value.cardboards:
				if key in self.terminator_piles:
					return True
				else:
					empty_piles += 1
		return empty_piles > 2

	def get_id(self) -> t.ByteString:
		return self.id_provider.get_id()

