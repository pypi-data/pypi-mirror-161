from typing import overload
from typing import List
from typing import TypeVar
from typing import Any
from typing import Generic

Function = TypeVar["java.util.function.Function_E,java.lang.Integer_"]
T = TypeVar("T")
E = TypeVar("E")
Queue = TypeVar["java.util.Queue_E_"]

class PrioryFiFoTaskQueue(Queue, Generic[E]):

	@overload
	def __init__(self, priorityFunction: Function) -> None:
		pass

	@overload
	def size(self) -> int:
		pass

	@overload
	def isEmpty(self) -> bool:
		pass

	@overload
	def contains(self, o: object) -> bool:
		pass

	@overload
	def iterator(self) -> iter:
		pass

	@overload
	def toArray(self) -> List[object]:
		pass

	@overload
	def toArray(self, ts: List[T]) -> List[T]:
		pass

	@overload
	def add(self, e: E) -> bool:
		pass

	@overload
	def remove(self, o: object) -> bool:
		pass

	@overload
	def containsAll(self, collection: List[Any]) -> bool:
		pass

	@overload
	def addAll(self, collection: List[Any]) -> bool:
		pass

	@overload
	def removeAll(self, collection: List[Any]) -> bool:
		pass

	@overload
	def retainAll(self, collection: List[Any]) -> bool:
		pass

	@overload
	def clear(self) -> None:
		pass

	@overload
	def offer(self, e: E) -> bool:
		pass

	@overload
	def remove(self) -> E:
		pass

	@overload
	def poll(self) -> E:
		pass

	@overload
	def pollWaiting(self) -> E:
		pass

	@overload
	def pollWaiting(self, timeout: float) -> E:
		pass

	@overload
	def peekWaiting(self) -> E:
		pass

	@overload
	def peekWaiting(self, timeout: float) -> E:
		pass

	@overload
	def element(self) -> E:
		pass

	@overload
	def peek(self) -> E:
		pass

	pass


