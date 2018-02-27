
from abc import abstractmethod

from eventtree.replaceevent import EventSession, Event

from throneloon.game.artifacts.artifact import GameObject, GameArtifact
from throneloon.game.artifacts.observation import GameObserver
from throneloon.game.artifacts.zones import Zone, Zoneable, ZoneFacingMode
from throneloon.game.values.currency import Price


class KingdomComponent(GameObject):

	@abstractmethod
	def setup(self, event: Event):
		pass


# class TopRevealedZone(Zone):
#
# 	def __init__(self, session: EventSession, owner: GameArtifact = None):
# 		super().__init__(session, owner, True, False, True)
#
# 	def join(self, zoneable: Zoneable):
# 		if self._zoneables:
# 			self._session.resolve_event(
# 				ge.TurnCardboard,
# 				target=self._zoneables[-1],
# 				face_up=False,
# 			)
# 		super().join(zoneable)
#
# 	def leave(self, zoneable: Zoneable):
# 		super().leave(zoneable)
# 		if self._zoneables:
# 			self._session.resolve_event(
# 				ge.TurnCardboard,
# 				target=self._zoneables[-1],
# 				face_up=True,
# 			)


class Pile(KingdomComponent):
	name = 'Abstract Base Pile' #type: str

	def __init__(self, session: EventSession):
		super().__init__(session)
		self._cardboards = Zone(
			session = session,
			facing_mode = ZoneFacingMode.STACK,
			ordered = True,
		)
		self._tokens = Zone(
			session = session,
			facing_mode = ZoneFacingMode.FACE_UP,
			ordered = True,
		)

	@property
	def cardboards(self) -> Zone:
		return self._cardboards

	@property
	def tokens(self) -> Zone:
		return self._tokens

	def setup(self, event: Event):
		pass

	def serialize(self, observer: GameObserver) -> str:
		return super().serialize(observer)


class BuyableEvent(KingdomComponent):

	def __init__(self, session: EventSession):
		super().__init__(session)
		self._price = None  # type: Price

	@abstractmethod
	def on_buy(self, event: Event):
		pass

	def serialize(self, observer: GameObserver) -> str:
		return super().serialize(observer)


class Landmark(KingdomComponent):

	@abstractmethod
	def on_game_end(self, event: Event):
		pass

	def serialize(self, observer: GameObserver) -> str:
		return super().serialize(observer)

