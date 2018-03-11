
from frozendict import frozendict

from throneloon.models import piles
from throneloon.models import buyableevents as bevs


class _FrozenDict(frozendict):

	def __add__(self, other):
		d = {}
		d.update(self)
		d.update(other)
		return _FrozenDict(d)


BASIC_SUPPLY = _FrozenDict(
	{
		'Copper': piles.CopperPile,
		'Silver': piles.SilverPile,
		'Gold': piles.GoldPile,
		'Estate': piles.EstatePile,
		'Duchy': piles.DuchyPile,
		'Province': piles.ProvincePile,
		'Curse': piles.CursePile,
	}
)

BASE_SET = _FrozenDict(
	{
		'Village': piles.VillagePile,
		'Cellar': piles.CellarPile,
		'Chapel': piles.ChapelPile,
		'Militia': piles.MilitiaPile,
		'Throne Room': piles.ThroneRoomPile,
		'Moat': piles.MoatPile,
	}
)

PROSPERITY = _FrozenDict(
	{
		'Watchtower': piles.WatchtowerPile,
		'Wharf': piles.WharfPile,
	}
)

HINTERLANDS = _FrozenDict(
	{
		'Trader': piles.TraderPile,
	}
)

INTRIGUE = _FrozenDict(
	{
		'Secret Chamber': piles.SecretChamberPile,
	}
)

CORNUCOPIA = _FrozenDict(
	{
		'Hamlet': piles.HamletPile,
	}
)

DARK_AGES = _FrozenDict(
	{
		'Band of Misfits': piles.BandOfMisfitsPile,
	}
)

NOCTURNE = _FrozenDict(
	{
		'Necromancer': piles.NecromancerPile,
		"Devil's Workshop": piles.DevilsWorkshopPile,
		"Secret Cave": piles.SecretCavePile,
	}
)


ADVENTURES_BUYABLE_EVENTS = _FrozenDict(
	{
		event.name: event for event in (
			bevs.Expedition,
		)
	}
)


ALL_NON_BASIC_PILES = BASE_SET + PROSPERITY + HINTERLANDS + INTRIGUE + CORNUCOPIA + DARK_AGES + NOCTURNE
ALL_PILES = ALL_NON_BASIC_PILES + BASE_SET
ALL_BUYABLE_EVENTS = ADVENTURES_BUYABLE_EVENTS