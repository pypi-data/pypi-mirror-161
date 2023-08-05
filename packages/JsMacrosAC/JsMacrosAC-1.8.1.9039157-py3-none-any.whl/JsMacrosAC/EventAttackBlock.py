from typing import overload
from .BaseEvent import BaseEvent
from .BlockDataHelper import BlockDataHelper


class EventAttackBlock(BaseEvent):
	block: BlockDataHelper
	side: int

	@overload
	def __init__(self, block: BlockDataHelper, side: int) -> None:
		pass

	pass


