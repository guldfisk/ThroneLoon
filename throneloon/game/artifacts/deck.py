import typing as t

from eventtree.replaceevent import Event

from throneloon.game.artifacts.artifact import IdSession
from throneloon.game.artifacts.zones import Zone, ZoneOwner, ZoneFacingMode
from throneloon.game.artifacts.cards import Cardboard


class Deck(object):

	def __init__(self, session: IdSession, event: Event, owner: t.Optional[ZoneOwner] = None) -> None:
		self._owner = owner
		self._library = Zone(
			session = session,
			event = event,
			owner =  owner,
			name = 'library',
			facing_mode = ZoneFacingMode.FACE_DOWN,
			owner_see_face_down = False,
			ordered = True,
		) #type: Zone[Cardboard]
		self._graveyard = Zone(
			session = session,
			event = event,
			owner =  owner,
			name = 'graveyard',
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		) #type: Zone[Cardboard]

	@property
	def library(self) -> Zone[Cardboard]:
		return self._library

	@property
	def graveyard(self) -> Zone[Cardboard]:
		return self._graveyard