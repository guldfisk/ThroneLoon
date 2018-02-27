import typing as t

from ordered_set import OrderedSet


class _RingLink(object):
	def __init__(self, content: object):
		self.content = content
		self.next = None #type: _RingLink
		self.previous = None #type: _RingLink


class Ring(object):
	def __init__(self, content: t.Iterable[t.Any]):
		self._raw_content = OrderedSet(content)
		self._content = tuple(_RingLink(content) for content in self._raw_content)
		for i in range(len(self._content)):
			self._content[i].next = self._content[(i+1)%len(self._content)]
			self._content[i].previous = self._content[i-1]
		try:
			self._current = self._content[-1]
		except IndexError:
			raise ValueError('Ring must contain at least one object')

	@property
	def all(self) -> OrderedSet:
		return self._raw_content

	def current(self):
		return self._current.content

	def next(self):
		self._current = self._current.next
		return self._current.content

	def previous(self):
		self._current = self._current.previous
		return self._current.content

	def peek_next(self):
		return self._current.next.content

	def peek_previous(self):
		return self._current.previous.content

	def __iter__(self):
		while True:
			yield self.next()

	def __len__(self):
		return self._content.__len__()

	def __eq__(self, other: object) -> bool:
		return isinstance(other, self.__class__) and self._raw_content == other._raw_content

	def __hash__(self) -> int:
		return hash(self._raw_content)
