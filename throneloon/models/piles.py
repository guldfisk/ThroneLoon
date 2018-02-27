

from throneloon.models.templates.piles import BasicSupplyPile, SupplyPile
from throneloon.models import cards

class CopperPile(BasicSupplyPile):
	CARD_TYPE = cards.Copper

	def _amount(self) -> int:
		return 60

class VillagePile(SupplyPile):
	CARD_TYPE = cards.Village