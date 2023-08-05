from typing import overload
from typing import TypeVar
from .MethodWrapper import MethodWrapper

T = TypeVar("T")

class IFWrapper:
	"""FunctionalInterface implementation for wrapping methods to match the language spec. An instance of this class is passed to scripts as the 'consumer' variable. Javascript:
language spec requires that only one thread can hold an instance of the language at a time,
so this implementation uses a non-preemptive priority queue for the threads that call the resulting MethodWrapper . JEP:
language spec requires everything to be on the same thread, on the java end, so all calls to MethodWrapper call back to JEP's starting thread and wait for the call to complete. Jython:
no limitations LUA:
no limitations\n
	Since: 1.2.5, re-named from 'consumer' in 1.3.2 
	"""

	@overload
	def methodToJava(self, c: T) -> MethodWrapper:
		"""
		Since: 1.4.0 

		Args:
			c: 

		Returns:
			a new MethodWrapper 
		"""
		pass

	@overload
	def methodToJavaAsync(self, c: T) -> MethodWrapper:
		"""
		Since: 1.4.0 

		Args:
			c: 

		Returns:
			a new MethodWrapper 
		"""
		pass

	@overload
	def methodToJavaAsync(self, priority: int, c: T) -> MethodWrapper:
		"""JS/JEP ONLY
allows you to set the position of the thread in the queue. you can use this for return value one's too...\n
		Since: 1.8.0 

		Args:
			A: 
			B: 
			R: 
			c: 
			priority: 
		"""
		pass

	@overload
	def deferCurrentTask(self) -> None:
		"""JS/JEP only, puts current task at end of queue.
use with caution, don't accidentally cause circular waiting.\n
		Since: 1.4.0 [citation needed] 
		"""
		pass

	@overload
	def deferCurrentTask(self, priorityAdjust: int) -> None:
		"""JS/JEP only, puts current task at end of queue.
use with caution, don't accidentally cause circular waiting.\n
		Since: 1.8.0 

		Args:
			priorityAdjust: the amount to adjust the priority by 
		"""
		pass

	@overload
	def getCurrentPriority(self) -> int:
		"""JS/JEP only, get priority of current task.\n
		Since: 1.8.0 
		"""
		pass

	@overload
	def stop(self) -> None:
		"""Close the current context\n
		Since: 1.2.2 
		"""
		pass

	pass


