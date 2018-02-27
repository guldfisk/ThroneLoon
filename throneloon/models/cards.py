from eventtree.replaceevent import Event

from eventtree.replaceevent import EventSession

from throneloon.game import gameevents as ge

from throneloon.models.templates.cards import Treasure, Action
from throneloon.game.artifacts.cards import Cardboard
from throneloon.game.values.currency import Value, Price


class Copper(Treasure):
	name = 'Copper'

	def __init__(self, session: EventSession, cardboard: Cardboard):
		super().__init__(session, cardboard)
		self._value = Value(session, self, 1)
		self._price = Price(session, self, 0)


class Village(Action):
	name = 'Village'

	def on_play(self, event: Event):
		event.spawn_tree(ge.AddAction, amount=2).resolve()