import typing as t

from throneloon.game.artifacts.artifact import IdSession
from throneloon.game.artifacts.zones import Zone, ZoneOwner, ZoneFacingMode


class Deck(object):

	def __init__(self, session: IdSession, owner: t.Optional[ZoneOwner]) -> None:
		self._owner = owner
		self._library = Zone(
			session = session,
			owner =  owner,
			name = 'library',
			facing_mode = ZoneFacingMode.FACE_DOWN,
			owner_see_face_down = False,
			ordered = True,
		)
		self._graveyard = Zone(
			session = session,
			owner =  owner,
			name = 'graveyard',
			facing_mode = ZoneFacingMode.FACE_UP,
			owner_see_face_down = False,
			ordered = True,
		)

	@property
	def library(self) -> Zone:
		return self._library

	@property
	def graveyard(self) -> Zone:
		return self._graveyard