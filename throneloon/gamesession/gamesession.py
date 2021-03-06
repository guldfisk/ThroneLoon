import typing as t

import random
import time
import threading

from multiprocessing import Process, Pipe

from throneloon.game.setup.setupinfo import SetupInfo
from throneloon.game.setup.kingdominfo import KingdomComponentInfo, KingdomInfo
from throneloon.game.game import Game
from throneloon.io.interface import IOInterface
from throneloon.game.idprovide import IdProvider
from throneloon.models import models

from throneloon.game import gameevents as ge


class GameSession(Process):

	def __init__(
		self,
		connection, #multiprocess pipe connection, can't import type
		interface: IOInterface,
		setup_info: t.Optional[SetupInfo] = None,
		seed: t.Optional[t.ByteString] = None,
	) -> None:
		super().__init__()
		self._connection = connection
		self._interface = interface
		self._setup_info = setup_info
		self._game = None #type: Game
		self._id_provider = None #type: IdProvider
		self._seed = str(hash(time.time())).encode('ASCII') if seed is None else seed #type: t.ByteString

	def run(self):
		random.seed(self._seed)

		kingdom_info = KingdomInfo(
			piles=(
				KingdomComponentInfo(name) for name in models.ALL_NON_BASIC_PILES
			),
			events=(
				KingdomComponentInfo(name) for name in models.ALL_BUYABLE_EVENTS
			)
		)

		setup_info = SetupInfo(kingdom_info, self._setup_info.num_players)

		self._id_provider = IdProvider(self._seed)

		self._game = Game(self._interface, self._id_provider)

		self._game.resolve_event(
			ge.Setup,
			info = setup_info,
			basic_supply = models.BASIC_SUPPLY,
			all_piles = models.ALL_NON_BASIC_PILES,
			all_buyable_events = models.ALL_BUYABLE_EVENTS,
		)

		self._game.resolve_event(ge.Play)