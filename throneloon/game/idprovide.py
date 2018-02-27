import typing as t
import hashlib
from itertools import count

class IdProvider(object):
	def __init__(self, seed: t.ByteString):
		self._counter = count()
		self._hashing =  hashlib.sha3_256()
		self._hashing.update(seed)
		self._previous_ids = set() #type: t.Set[str]

	def get_id(self):
		while True:
			self._hashing.update(
				str(self._counter.__next__()).encode('ASCII')
			)
			_id = self._hashing.hexdigest()
			if not _id in self._previous_ids:
				break
		self._previous_ids.add(_id)
		return _id