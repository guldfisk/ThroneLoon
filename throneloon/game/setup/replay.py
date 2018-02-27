import typing as t

from throneloon.game.setup.setupinfo import SetupInfo

class Replay(object):
	def __init__(
		self,
		setup_info: SetupInfo,
		random_seed: t.ByteString,
		actions: t.Tuple[str, ...],
	):
		self._setup_info = setup_info
		self._random_seed = random_seed
		self._actions = actions

	@property
	def setup_info(self) -> SetupInfo:
		return self._setup_info

	@property
	def random_seed(self) -> t.ByteString:
		return self._random_seed

	@property
	def actions(self) -> t.Tuple[str, ...]:
		return self._actions

	def __hash__(self):
		return hash((self._setup_info, self._random_seed, self._actions))

	def __eq__(self, other):
		return (
			isinstance(other, self.__class__)
			and self._setup_info == other.setup_info
			and self._random_seed == other.random_seed
			and self._actions == other.actions
		)