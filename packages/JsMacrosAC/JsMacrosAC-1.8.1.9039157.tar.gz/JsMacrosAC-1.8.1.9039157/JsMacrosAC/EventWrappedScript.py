from typing import overload
from typing import TypeVar
from typing import Generic
from .BaseEvent import BaseEvent

R = TypeVar("R")
T = TypeVar("T")
U = TypeVar("U")

class EventWrappedScript(BaseEvent, Generic[T, U, R]):
	"""
	Since: 1.7.0 
	"""
	arg1: T
	arg2: U
	result: R

	@overload
	def __init__(self, arg1: T, arg2: U) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def setReturnBoolean(self, b: bool) -> None:
		pass

	@overload
	def setReturnInt(self, i: int) -> None:
		pass

	@overload
	def setReturnDouble(self, d: float) -> None:
		pass

	@overload
	def setReturnString(self, s: str) -> None:
		pass

	@overload
	def setReturnObject(self, o: object) -> None:
		pass

	pass


