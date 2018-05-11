import typing as t

from enum import Enum

from collections import Iterable

from ordered_set import OrderedSet

from eventtree.replaceevent import Condition, Event

from throneloon.game.artifacts.artifact import GameArtifact, GameObject, IdSession
from throneloon.game.artifacts.mats import Mat
from throneloon.game.artifacts.observation import GameObserver, serialization_values
from throneloon.game.artifacts.zones import Zone, ZoneOwner, ZoneFacingMode, Zoneable
from throneloon.game.artifacts.cards import Cardboard
from throneloon.game.artifacts.tokens import Token
from throneloon.game.artifacts.states import State
from throneloon.game.artifacts.deck import Deck
from throneloon.game.values.currency import CurrencyValue
from throneloon.io.interface import IOInterface, io_options, io_option

from throneloon.utils.containers.frozendict import FrozenDict


picking_options = t.Union[Zone, t.Iterable[str], t.Callable[[], io_options]]


class AdditionalOption(object):

	def __init__(self, option: t.Union[GameArtifact, str], action: t.Callable, reason: t.Optional[str] = None):
		self.option = option  # type: t.Union[GameArtifact, str, Condition]
		self.action = action  # type: t.Callable[None, None]
		self.reason = reason  # type: t.Optional[str]


class AdditionalOptionTreatment(Enum):
	MERGE = 'merge'
	RESOLVE = 'resolve'
	IGNORE = 'ignore'


class OptionPicker(object):

	def __init__(self, interface: IOInterface, player: 'Player') -> None:
		super().__init__()

		self._interface = interface  # type: IOInterface
		self._player = player  # type: Player

		self._additional_options = {}  # type: t.Dict[t.Union[GameArtifact, str], AdditionalOption]

	def add_additional_option(self, option: AdditionalOption) -> 'OptionPicker':
		self._additional_options[option.option] = option
		return self

	def additional_options_pending(self) -> bool:
		return bool(self._additional_options)

	def order_options(
		self,
		options: picking_options,
		add_opp_treatment: AdditionalOptionTreatment = AdditionalOptionTreatment.RESOLVE,
		reason: t.Optional[str] = None,
	) -> t.List[io_option]:
		return self.pick_options(
			options = options,
			minimum = None,
			maximum = None,
			add_opp_treatment = add_opp_treatment,
			reason = reason,
		)

	def pick_option(
		self,
		options: picking_options,
		optional: bool = False,
		add_opp_treatment: AdditionalOptionTreatment = AdditionalOptionTreatment.RESOLVE,
		reason: t.Optional[str] = None
	) -> t.Optional[io_option]:
		options = self.pick_options(
			options = options,
			minimum = 0 if optional else 1,
			maximum = 1,
			add_opp_treatment = add_opp_treatment,
			reason = reason,
		)
		return options[0] if options else None

	def pick_options(
		self,
		options: picking_options,
		minimum: t.Optional[int] = 1,
		maximum: t.Optional[int] = None,
		add_opp_treatment: AdditionalOptionTreatment = AdditionalOptionTreatment.RESOLVE,
		reason: t.Optional[str] = None,
	) -> t.List[io_option]:

		end_additional_options = 'End additional actions'

		if add_opp_treatment == AdditionalOptionTreatment.RESOLVE and self._additional_options:
			while self._additional_options:
				result = self._interface.select_option(
					player = self._player,
					options = [end_additional_options],
					additional_options = {
						option: self._additional_options[option].reason
						for option in
						self._additional_options
					},
					reason=reason,
				)
				if result == end_additional_options:
					break
				self._additional_options.pop(result).action()

		if isinstance(options, Zone):
			_option_retriever = lambda : options
		elif isinstance(options, Iterable):
			_option_tuple = tuple(options)
			_option_retriever = lambda : _option_tuple
		else:
			_option_retriever = options

		while True:
			returned_options = _option_retriever()
			if not returned_options and not self._additional_options:
				return []
			_options = list(returned_options) if returned_options else [end_additional_options]
			if len(_options) <= minimum and not self._additional_options:
				return _options
			result = self._interface.select_options(
				player = self._player,
				options = _options,
				minimum = minimum,
				maximum = maximum,
				additional_options = (
					{}
					if add_opp_treatment == AdditionalOptionTreatment.IGNORE else
					{
						option: self._additional_options[option].reason
						for option in
						self._additional_options
					}
				),
				reason = reason,
			)
			if not isinstance(result, list):
				self._additional_options.pop(result).action()
			else:
				if add_opp_treatment == AdditionalOptionTreatment.MERGE:
					self._additional_options = {}
				return result


class Player(GameObject, ZoneOwner, GameObserver):

	def __init__(self, session: IdSession, event: Event, interface: IOInterface, id: t.ByteString):
		super().__init__(session, event)

		self.id = id

		self._picker = OptionPicker(interface, self)

		self._zones = OrderedSet() #type: t.Set[Zone]

		self._currency = CurrencyValue()
		self.actions = 0
		self.buys = 0

		self._mats = {} #type: t.Dict[str, Mat]

		self._deck = Deck(
			session = session,
			event = event,
			owner = self,
		) #type: Deck

		self._hand = Zone(
			session = session,
			event = event,
			owner = self,
			name = 'hand',
			facing_mode = ZoneFacingMode.FACE_DOWN,
			owner_see_face_down = True,
			ordered = False,
		) #type: Zone[Cardboard]
		self._battlefield = Zone(
			session = session,
			event = event,
			owner = self,
			name = 'battlefield',
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		) #type: Zone[Cardboard]

		self._tokens = Zone(
			session = session,
			event = event,
			owner = self,
			name = 'tokens',
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		) #type: Zone[Token]
		self._states = Zone(
			session = session,
			event = event,
			owner = self,
			name = 'states',
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		) #type: Zone[State]

		self._peeking = [] #type: t.List[Zoneable]

	@property
	def peeking(self) -> t.List[GameArtifact]:
		return self._peeking

	@property
	def zones(self) -> 't.Set[Zone]':
		return self._zones

	@property
	def deck(self) -> Deck:
		return self._deck

	@property
	def currency(self) -> CurrencyValue:
		return self._currency

	@currency.setter
	def currency(self, value: CurrencyValue) -> None:
		self._currency = value

	@property
	def mats(self) -> t.Dict[str, Mat]:
		return self._mats

	@property
	def library(self) -> Zone[Cardboard]:
		return self._deck.library

	@property
	def hand(self) -> Zone[Cardboard]:
		return self._hand

	@property
	def battlefield(self) -> Zone[Cardboard]:
		return self._battlefield

	@property
	def graveyard(self) -> Zone[Cardboard]:
		return self._deck.graveyard

	@property
	def tokens(self) -> Zone[Token]:
		return self._tokens

	@property
	def states(self) -> Zone[State]:
		return self._states

	def order_options(
		self,
		options: picking_options,
		add_opp_treatment: AdditionalOptionTreatment = AdditionalOptionTreatment.RESOLVE,
		reason: t.Optional[str] = None,
	) -> t.List[io_option]:
		return self._picker.order_options(
			options = options,
			add_opp_treatment = add_opp_treatment,
			reason = reason,
		)

	def pick_option(
		self,
		options: picking_options,
		optional: bool = False,
		add_opp_treatment: AdditionalOptionTreatment = AdditionalOptionTreatment.RESOLVE,
		reason: t.Optional[str] = None
	) -> t.Optional[io_option]:
		return self._picker.pick_option(
			options = options,
			optional = optional,
			add_opp_treatment = add_opp_treatment,
			reason = reason,
		)

	def pick_options(
		self,
		options: picking_options,
		minimum: int = 1,
		maximum: t.Optional[int] = None,
		add_opp_treatment: AdditionalOptionTreatment = AdditionalOptionTreatment.RESOLVE,
		reason: t.Optional[str] = None,
	) -> t.List[io_option]:
		return self._picker.pick_options(
			options = options,
			minimum = minimum,
			maximum = maximum,
			add_opp_treatment = add_opp_treatment,
			reason = reason
		)

	def resolve_add_ops(self):
		self._picker.pick_options(
			options = [],
			minimum = 0,
			add_opp_treatment = AdditionalOptionTreatment.MERGE,
			reason = 'Choose additional action',
		)

	def register_additional_option(
		self,
		option: t.Union[str, GameArtifact],
		action: t.Callable,
		reason: t.Optional[str] = None,
	) -> None:
		self._picker.add_additional_option(
			AdditionalOption(
				option,
				action,
				reason,
			)
		)

	def has_additional_options(self) -> bool:
		return self._picker.additional_options_pending()

	def serialize(self, player: GameObserver) -> serialization_values:
		return super().serialize(player) + FrozenDict(
			{
				'id': self._id,
			}
		)

	def __repr__(self) -> str:
		return '{}({})'.format(
			self.__class__.__name__,
			self.id[-4:-1],
		)

