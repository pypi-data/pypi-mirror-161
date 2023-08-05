from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .EntityHelper import EntityHelper

Entity = TypeVar["net.minecraft.entity.Entity"]

class EventInteractEntity(BaseEvent):
	offhand: bool
	result: str
	entity: EntityHelper

	@overload
	def __init__(self, offhand: bool, resultStatus: str, entity: Entity) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


