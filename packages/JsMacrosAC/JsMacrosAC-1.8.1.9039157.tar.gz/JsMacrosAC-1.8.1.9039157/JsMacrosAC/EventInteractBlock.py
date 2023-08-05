from typing import overload
from .BaseEvent import BaseEvent
from .BlockDataHelper import BlockDataHelper


class EventInteractBlock(BaseEvent):
	"""
	Since: 1.8.0 
	"""
	offhand: bool
	result: str
	block: BlockDataHelper
	side: int

	@overload
	def __init__(self, offhand: bool, resultStatus: str, block: BlockDataHelper, side: int) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


