
from eventtree.replaceevent import DelayedReplacement

from throneloon.game.artifacts.kingdomcomponents import BuyableEvent
from throneloon.game.values.currency import Price
from throneloon.game.artifacts.observation import GameObserver
from throneloon.game.artifacts.artifact import IdSession
from throneloon.game import gameevents as ge

class Expedition(BuyableEvent):
	name = 'Expedition'

	def __init__(self, session: IdSession, event: ge.CreateBuyableEvent):
		super().__init__(session, event)

		self._price = Price(session, self, 3)

	def on_buy(self, event: ge.BuyBuyableEvent):
		self.create_condition(
			DelayedReplacement,
			parent = event,
			trigger = 'DrawHand',
			condition = lambda source: source.player==event.player,
			replace = lambda source: source.replace_clone(amount=source.amount+2),
		)

	def serialize(self, observer: GameObserver) -> str:
		return super().serialize(observer)

