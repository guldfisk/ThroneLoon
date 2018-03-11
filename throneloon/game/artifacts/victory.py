
from abc import abstractmethod, ABCMeta

class VictoryValuable(object, metaclass=ABCMeta):

	@property
	@abstractmethod
	def vp_value(self) -> int:
		pass