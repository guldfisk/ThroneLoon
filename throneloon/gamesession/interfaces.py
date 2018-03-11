import typing as t
import re

from eventtree.replaceevent import Event, Condition

from throneloon.game.artifacts.players import Player
from throneloon.game.artifacts.artifact import GameArtifact
from throneloon.io.interface import IOInterface


class DummyInterface(IOInterface):

	def __init__(self):
		self._indentation_levels = {} #type: t.Dict[Event, int]

	@staticmethod
	def _stringify(option: t.Union[GameArtifact, str, Condition]):
		if isinstance(option, GameArtifact):
			return option.name
		elif isinstance(option, Condition):
			return option.source.name
		else:
			return option

	def select_option(
		self,
		player: Player,
		options: t.Iterable[t.Union[GameArtifact, str, Condition]],
		optional: bool = False,
		additional_options: t.Optional[t.Dict[t.Union[GameArtifact, str, Condition], t.Optional[str]]] = None,
		reason: t.Optional[str] = None,
	) -> t.Union[GameArtifact, str, Condition]:
		options = self.select_options(
			player = player,
			options = options,
			minimum = 0 if optional else 1,
			maximum = 1,
			reason = reason,
		)
		return options if options is None else options[0]


	def select_options(
		self,
		player: Player,
		options: t.Iterable[t.Union[GameArtifact, str, Condition]],
		minimum: t.Optional[int] = 1,
		maximum: t.Optional[int] = None,
		additional_options: t.Optional[t.Dict[t.Union[GameArtifact, str, Condition], t.Optional[str]]] = None,
		reason: t.Optional[str] = None,
	) -> t.Union[t.List[t.Union[GameArtifact, str, Condition]], t.Union[GameArtifact, str]]:

		_additional_options_in = additional_options if additional_options is not None else {}

		_options = list(options)

		_additional_options = {
			self._stringify(option): option
			for option in _additional_options_in
		}


		_maximum = len(_options) if maximum is None else maximum
		_minimum = len(_options) if minimum is None else minimum

		end_picks = 'finished selecting'

		picked = []
		for _ in range(_maximum):
			print(
				str(player)
				+(
					': ({}) '.format(picked)
					if _maximum > 1 else
					''
				)
				+', options: '
				+ str(
					[self._stringify(option) for option in _options]
					+ (
						[end_picks]
						if len(picked) > _minimum else
						[]
					)
				)
				+ (
					(
						' additional options: '
						+ str(
							[
								self._stringify(key)
								+ (
									''
									if value is None else
									': ' + value
								)
								for key, value in _additional_options_in.items()
							]
						)
					) if not picked else ''
				)
				+ (
					', ' + reason
					if reason else
					''
				)
				+ ' | A: {}, B: {}, C: {}, h: {}, b: {}, l: {}, y: {}'.format(
					player.actions,
					player.buys,
					player.currency,
					len(player.hand),
					len(player.battlefield),
					len(player.library),
					len(player.graveyard),
				)
			)

			_inspection_options = {
				'hand': player.hand,
				'field': player.battlefield,
				'lib': player.library,
				'yard': player.graveyard,
			}

			_looping = True
			last_valid = True
			choice = ''
			while _looping:
				force_add_op = False

				choice = input(('' if last_valid else '"{}" invalid'.format(choice))+': ')

				if choice in _inspection_options:
					print(list(_inspection_options[choice]))
					last_valid = True
					continue

				if choice and choice[0] == '-':
					choice = choice[1:]
					force_add_op = True

				pattern = re.compile(choice, re.IGNORECASE)

				if len(picked) > _minimum and choice and pattern.match(end_picks):
					return picked

				if not force_add_op:
					for i in range(len(_options)):
						if pattern.match(self._stringify(_options[i])):
							picked.append(_options.pop(i))
							_looping = False
							break

				if not picked:
					for key in _additional_options:
						if pattern.match(key):
							return _additional_options[key]

				last_valid = False

		return picked

	def notify_event(self, event: Event) -> None:

		if event.parent is None or event.parent not in self._indentation_levels:
			self._indentation_levels[event] = _indentation_level = 0
		else:
			self._indentation_levels[event] = _indentation_level = self._indentation_levels[event.parent] + 1

		print(
			'|'+'-|'*_indentation_level+'{}: {}'.format(
				event.__class__.__name__,
				event.values,
			)

		)