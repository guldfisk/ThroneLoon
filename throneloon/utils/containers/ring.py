import typing as t

from collections import OrderedDict
from ordered_set import OrderedSet


T = t.TypeVar('T')


class _RingLink(object):
	def __init__(self, content: object):
		self.content = content
		self.next = None #type: _RingLink
		self.previous = None #type: _RingLink


class Ring(t.Generic[T]):
	def __init__(self, content: t.Iterable[T]):
		self._raw_content = OrderedSet(content)
		self._content = OrderedDict(
			{content: _RingLink(content) for content in self._raw_content}
		)
		_content = tuple(self._content.values())
		for i in range(len(_content)):
			_content[i].next = _content[(i+1)%len(_content)]
			_content[i].previous = _content[i-1]
		try:
			self._current = _content[-1]
		except IndexError:
			raise ValueError('Ring must contain at least one object')

	@property
	def all(self) -> OrderedSet:
		return self._raw_content

	def current(self) -> T:
		return self._current.content

	def next(self) -> T:
		self._current = self._current.next
		return self._current.content

	def previous(self) -> T:
		self._current = self._current.previous
		return self._current.content

	def peek_next(self) -> T:
		return self._current.next.content

	def peek_previous(self) -> T:
		return self._current.previous.content

	def loop_from(self, start: t.Any) -> t.Iterable[T]:
		link = self._content[start]
		while True:
			yield link.content
			link = link.next
			if link.content == start:
				break

	def __iter__(self) -> t.Iterable[T]:
		while True:
			yield self.next()

	def __len__(self):
		return self._content.__len__()

	def __eq__(self, other: object) -> bool:
		return isinstance(other, self.__class__) and self._raw_content == other._raw_content
