import typing as t

from eventtree.replaceevent import Attributed, EventSession

from throneloon.game.artifacts.artifact import GameArtifact


class CurrencyValue(object):
	def __init__(
		self,
		coin_value: int = 0,
		potion_value: int = 0,
		debt_value: int = 0,
	):
		self._prices = {
			'coin_value': coin_value,
			'potion_value': potion_value,
			'debt_value': debt_value,
		}

	@property
	def coin_value(self) -> int:
		return self._prices['coin_value']

	@coin_value.setter
	def coin_value(self, value: int) -> None:
		self._prices['coin_value'] = value

	@property
	def potion_value(self) -> int:
		return self._prices['potion_value']

	@potion_value.setter
	def potion_value(self, value: int) -> None:
		self._prices['potion_value'] = value

	@property
	def debt_value(self) -> int:
		return self._prices['debt_value']

	@debt_value.setter
	def debt_value(self, value: int) -> None:
		self._prices['debt_value'] = value

	def can_pay(self, price: 'CurrencyValue') -> bool:
		return (
			self.debt_value <= 0
			and self.coin_value >= price.coin_value
			and self.potion_value >= price.potion_value
		)

	def pay(self, price: 'CurrencyValue') -> 'CurrencyValue':
		self.coin_value -= price.coin_value
		self.potion_value -= price.potion_value
		self.debt_value += price.debt_value
		return self

	def __eq__(self, other):
		return all(self._prices[key] == other._prices[key] for key in self._prices)

	def __gt__(self, other):
		return (
			any(self._prices[key] > other._prices[key] for key in self._prices)
			and all(self._prices[key] >= other._prices[key] for key in self._prices)
		)

	def __ge__(self, other):
		return all(self._prices[key] >= other._prices[key] for key in self._prices)

	def __lt__(self, other):
		return (
			any(self._prices[key] < other._prices[key] for key in self._prices)
			and all(self._prices[key] <= other._prices[key] for key in self._prices)
		)

	def __le__(self, other):
		return all(self._prices[key] <= other._prices[key] for key in self._prices)

	def __add__(self, other):
		return CurrencyValue(
			self.coin_value + other.coin_value,
			self.potion_value + other.potion_value,
			self.debt_value + other.debt_value,
		)

	def __sub__(self, other):
		return CurrencyValue(
			self.coin_value - other.coin_value,
			self.potion_value - other.potion_value,
			self.debt_value - other.debt_value,
		)

	def __repr__(self):
		return '{}(c: {}, p: {}, d: {})'.format(
			self.__class__.__name__,
			self.coin_value,
			self.potion_value,
			self.debt_value
		)


class Price(Attributed):
	def __init__(
		self,
		session: EventSession,
		owner: GameArtifact = None,
		coin_price: int = 0,
		potion_price: int = 0,
		debt_price: int = 0,
	):
		super().__init__(session)

		self._owner = owner

		self._coin_price = self.pa('coin_price', coin_price)
		self._potion_price = self.pa('potion_price', potion_price)
		self._debt_price = self.pa('debt_price', debt_price)

	@property
	def owner(self) -> 't.Optional[GameArtifact]':
		return self._owner

	@property
	def coin_price(self) -> int:
		return self._coin_price.get()

	@property
	def potion_price(self) -> int:
		return self._potion_price.get()

	@property
	def debt_price(self) -> int:
		return self._debt_price.get()

	@property
	def value(self) -> CurrencyValue:
		return CurrencyValue(self.coin_price, self.potion_price, self.debt_price)


class Value(Attributed):
	def __init__(
		self,
		session: EventSession,
		owner: GameArtifact = None,
		coin_value: int = 0,
		potion_value: int = 0,
	):
		super().__init__(session)
		self._owner = owner
		self._coin_value = self.pa('coin_value', coin_value)
		self._potion_value = self.pa('potion_value', potion_value)

	@property
	def owner(self) -> 't.Optional[GameArtifact]':
		return self._owner

	@property
	def coin_value(self) -> int:
		return self._coin_value.get()

	@property
	def potion_value(self) -> int:
		return self._potion_value.get()

	@property
	def value(self) -> CurrencyValue:
		return CurrencyValue(self.coin_value, self.potion_value, 0)