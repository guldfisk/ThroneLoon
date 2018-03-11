
from eventtree.replaceevent import Event, Replacement

from throneloon.game import gameevents as ge
from throneloon.models.templates.piles import BasicSupplyPile, SupplyPile, VictorySupplyPile, HeirloomPile
from throneloon.models import cards


class CopperPile(BasicSupplyPile):
	CARD_TYPE = cards.Copper

	def _amount(self, event: ge.CreatePile) -> int:
		return 60


class SilverPile(BasicSupplyPile):
	CARD_TYPE = cards.Silver

	def _amount(self, event: ge.CreatePile) -> int:
		return 40


class GoldPile(BasicSupplyPile):
	CARD_TYPE = cards.Gold

	def _amount(self, event: ge.CreatePile) -> int:
		return 30


class EstatePile(VictorySupplyPile):
	CARD_TYPE = cards.Estate

	def _amount(self, event: ge.CreatePile) -> int:
		return super()._amount(event) + len(event._session.players) * 3


class DuchyPile(VictorySupplyPile):
	CARD_TYPE = cards.Duchy


class ProvincePile(VictorySupplyPile):
	CARD_TYPE = cards.Province

	def _amount(self, event: ge.CreatePile) -> int:
		return 1


class CursePile(BasicSupplyPile):
	CARD_TYPE = cards.Curse

	def _amount(self, event: ge.CreatePile) -> int:
		return 10


class VillagePile(SupplyPile):
	CARD_TYPE = cards.Village


class CellarPile(SupplyPile):
	CARD_TYPE = cards.Cellar


class ChapelPile(SupplyPile):
	CARD_TYPE = cards.Chapel


class MoatPile(SupplyPile):
	CARD_TYPE = cards.Moat


class MilitiaPile(SupplyPile):
	CARD_TYPE = cards.Militia


class ThroneRoomPile(SupplyPile):
	CARD_TYPE = cards.ThroneRoom


class WatchtowerPile(SupplyPile):
	CARD_TYPE = cards.Watchtower


class WharfPile(SupplyPile):
	CARD_TYPE = cards.Wharf


class TraderPile(SupplyPile):
	CARD_TYPE = cards.Trader


class SecretChamberPile(SupplyPile):
	CARD_TYPE = cards.SecretChamber


class HamletPile(SupplyPile):
	CARD_TYPE = cards.Hamlet


class NecromancerPile(SupplyPile):
	CARD_TYPE = cards.Necromancer

	def setup(self, event: ge.CreatePile):
		super().setup(event)
		event.spawn_tree(ge.CreateCardboard, card_type=cards.ZombieApprentice, to=event.game.trash)
		event.spawn_tree(ge.CreateCardboard, card_type=cards.ZombieMason, to=event.game.trash)
		event.spawn_tree(ge.CreateCardboard, card_type=cards.ZombieSpy, to=event.game.trash)


class ImpPile(BasicSupplyPile):
	CARD_TYPE = cards.Imp

	def _amount(self, event: ge.CreatePile) -> int:
		return 13


class DevilsWorkshopPile(SupplyPile):
	CARD_TYPE = cards.DevilsWorkshop

	def setup(self, event: ge.CreatePile):
		super().setup(event)
		event.spawn_tree(ge.RequireNonSupplyPile, pile_type=ImpPile)


class WishPile(BasicSupplyPile):
	CARD_TYPE = cards.Wish

	def _amount(self, event: ge.CreatePile) -> int:
		return 12


class SecretCavePile(HeirloomPile):
	CARD_TYPE = cards.SecretCave
	HEIRLOOM_TYPE = cards.MagicLamp

	def setup(self, event: ge.CreatePile):
		super().setup(event)
		event.spawn_tree(ge.RequireNonSupplyPile, pile_type=WishPile)


class BandOfMisfitsPile(SupplyPile):
	CARD_TYPE = cards.BandOfMisfits