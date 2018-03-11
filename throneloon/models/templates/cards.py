from eventtree.replaceevent import EventSession, Replacement, DelayedTrigger

from throneloon.game.artifacts.cards import Card, Cardboard
from throneloon.game.artifacts.turns import Turn
from throneloon.game.values.cardtypes import TypeLine, CardType
from throneloon.game.values.currency import Value
from throneloon.game import gameevents as ge


class Action(Card):

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._type_line += CardType.ACTION

	def on_play(self, event: ge.ResolveCardboard):
		pass


class Treasure(Card):

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._type_line += CardType.TREASURE
		self._value = None #type: Value

	def on_play(self, event: ge.ResolveCardboard):
		event.spawn_tree(ge.AddCurrency, amount=self._value.value)


class Victory(Card):

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._type_line += CardType.VICTORY
		self._vp_value = None #type: int

	@property
	def vp_value(self) -> int:
		return self._vp_value

	def on_play(self, event: ge.ResolveCardboard):
		pass


class Duration(Card):

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._type_line += CardType.DURATION

		self._played_on = None #type: Turn

		self.create_condition(
			Replacement,
			parent = event,
			trigger = 'Destroy',
			condition = lambda destroy_event:
				destroy_event.target==self.cardboard and self.prevent_discard(destroy_event),
		)

	def on_play(self, event: ge.ResolveCardboard):
		self._played_on = event.game.turn_order.current_turn()
		self.create_condition(
			DelayedTrigger,
			parent = event,
			trigger = 'Upkeep',
			condition = lambda upkeep_event: upkeep_event.player == event.player,
			resolve = lambda upkeep_event: self.next_turn(upkeep_event),
		)

	def prevent_discard(self, event: ge.GameEvent) -> bool:
		return self._played_on == event.game.turn_order.current_turn()

	def next_turn(self, event: ge.Upkeep):
		pass

	def need_tre(self, event: ge.GameEvent) -> bool:
		return self.prevent_discard(event)


class Night(Card):

	def __init__(self, session: EventSession, cardboard: Cardboard, event: ge.CreateCardboard):
		super().__init__(session, cardboard, event)
		self._type_line += CardType.NIGHT

	def on_play(self, event: ge.ResolveCardboard):
		pass