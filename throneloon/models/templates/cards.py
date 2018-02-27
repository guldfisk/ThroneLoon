from eventtree.replaceevent import EventSession, Event

from throneloon.game.artifacts.cards import Card, Cardboard
from throneloon.game.values.cardtypes import TypeLine, CardType
from throneloon.game.values.currency import Value
from throneloon.game import gameevents as ge


class Action(Card):

	def __init__(self, session: EventSession, cardboard: Cardboard):
		super().__init__(session, cardboard)
		self._type_line += TypeLine((CardType.ACTION,))

class Treasure(Card):

	def __init__(self, session: EventSession, cardboard: Cardboard):
		super().__init__(session, cardboard)
		self._type_line += TypeLine((CardType.TREASURE,))
		self._value = None #type: Value

	def on_play(self, event: Event):
		event.spawn_tree(ge.AddCurrency, amount=self._value.value).resolve()
