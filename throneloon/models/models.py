
from throneloon.models import piles
from throneloon.models import buyableevents as bevs

from throneloon.utils.containers.frozendict import FrozenDict


BASIC_SUPPLY = FrozenDict(
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

BASE_SET = FrozenDict(
	{
		'Village': piles.VillagePile,
		'Cellar': piles.CellarPile,
		'Chapel': piles.ChapelPile,
		'Militia': piles.MilitiaPile,
		'Throne Room': piles.ThroneRoomPile,
		'Moat': piles.MoatPile,
	}
)

PROSPERITY = FrozenDict(
	{
		'Watchtower': piles.WatchtowerPile,
		'Wharf': piles.WharfPile,
	}
)

HINTERLANDS = FrozenDict(
	{
		'Trader': piles.TraderPile,
	}
)

INTRIGUE = FrozenDict(
	{
		'Secret Chamber': piles.SecretChamberPile,
	}
)

CORNUCOPIA = FrozenDict(
	{
		'Hamlet': piles.HamletPile,
	}
)

DARK_AGES = FrozenDict(
	{
		'Band of Misfits': piles.BandOfMisfitsPile,
	}
)

NOCTURNE = FrozenDict(
	{
		'Necromancer': piles.NecromancerPile,
		"Devil's Workshop": piles.DevilsWorkshopPile,
		"Secret Cave": piles.SecretCavePile,
	}
)


ADVENTURES_BUYABLE_EVENTS = FrozenDict(
	{
		event.name: event for event in (
			bevs.Expedition,
		)
	}
)


ALL_NON_BASIC_PILES = BASE_SET + PROSPERITY + HINTERLANDS + INTRIGUE + CORNUCOPIA + DARK_AGES + NOCTURNE
ALL_PILES = ALL_NON_BASIC_PILES + BASE_SET
ALL_BUYABLE_EVENTS = ADVENTURES_BUYABLE_EVENTS