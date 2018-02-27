import typing as t

from eventtree.replaceevent import EventSession, Attributed

from throneloon.game.idprovide import IdProvider
from throneloon.game.setup.setupinfo import SetupInfo
from throneloon.game.artifacts.turns import TurnOrder
from throneloon.game.artifacts.kingdomcomponents import Pile, BuyableEvent, Landmark
from throneloon.game.artifacts.mats import Mat
from throneloon.game.artifacts.zones import Zone
from throneloon.game.artifacts.players import Player


class Game(EventSession, Attributed):
	def __init__(self):
		EventSession.__init__(self)
		self.id_provider = None #type: IdProvider

		self.turn_order = None #type: TurnOrder

		self._supply_piles = {} #type: t.Dict[str, Pile]
		self._non_supply_piles = {} #type: t.Dict[str, Pile]
		self.buyable_events = {} #type: t.Dict[str, BuyableEvent]
		self.landmarks = {} #type: t.Dict[str, Landmark]

		self._mats = {} #type: t.Dict[str, Mat]
		self._tokens = Zone(self, None, True, False, False)

		self._boons = Zone(self, None, True, False, False)
		self._hexes = Zone(self, None, True, False, False)

	@property
	def players(self) -> t.Sequence[Player]:
		return self.turn_order.players

	@property
	def supply_piles(self) -> t.Dict[str, Pile]:
		return self._supply_piles

	@property
	def non_supply_piles(self) -> t.Dict[str, Pile]:
		return self._non_supply_piles

	# def start(self, info: SetupInfo, seed: t.Optional[t.ByteString] = None):
	# 	self.resolve_event(ge.Setup, info=info, seed=seed)

