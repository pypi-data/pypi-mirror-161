from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .EntityHelper import EntityHelper

Entity = TypeVar["net.minecraft.entity.Entity"]

class EventAttackEntity(BaseEvent):
	entity: EntityHelper

	@overload
	def __init__(self, entity: Entity) -> None:
		pass

	pass


