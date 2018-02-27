
from frozendict import frozendict

from throneloon.models import piles


class _FrozenDict(frozendict):

	def __add__(self, other):
		d = {}
		d.update(self)
		d.update(other)
		return _FrozenDict(d)


BASIC_SUPPLY = _FrozenDict(
	{
		'Copper': piles.CopperPile,
	}
)

BASE_SET = _FrozenDict(
	{
		'Village': piles.VillagePile,
	}
)


ALL_PILES = BASIC_SUPPLY + BASE_SET