import typing as t

from enum import Enum

class CardType(Enum):
	ACTION = 'action'
	TREASURE = 'treasure'
	VICTORY = 'victory'
	CURSE = 'curse'
	ATTACK = 'attack'
	REACTION = 'reaction'
	DURATION = 'duration'
	RESERVE = 'reserve'
	TRAVELER = 'traveler'
	GATHERING = 'gathering'
	CASTLE = 'castle'
	NIGHT = 'night'
	FATE = 'fate'
	DOOM = 'doom'
	HEIRLOOM = 'heirloom'
	SPIRIT = 'spirit'
	ZOMBIE = 'zombie'

class TypeLine(object):
	def __init__(self, card_types: t.Iterable[CardType]):
		self._card_types = frozenset(card_types)

	def __hash__(self):
		return hash(self._card_types)

	def __eq__(self, other):
		return (
			isinstance(other, self.__class__)
			and self._card_types == other._card_types
		)

	def __iter__(self):
		return self._card_types.__iter__()

	def __add__(self, other):
		if isinstance(other, CardType):
			return CardType(list(self._card_types)+[other])
		elif isinstance(other, self.__class__):
			return TypeLine(list(self._card_types) + list(other._card_types))
		raise TypeError()