from typing import overload
from typing import TypeVar
from typing import Mapping
from typing import Generic
from .Extension import Extension
from .Core import Core
from .ScriptTrigger import ScriptTrigger
from .BaseEvent import BaseEvent
from .EventContainer import EventContainer
from .BaseLibrary import BaseLibrary

T = TypeVar("T")
Consumer = TypeVar["java.util.function.Consumer_java.lang.Throwable_"]
U = TypeVar("U")
Runnable = TypeVar["java.lang.Runnable"]
File = TypeVar["java.io.File"]

class BaseLanguage(Generic[U, T]):
	"""Language class for languages to be implemented on top of.\n
	Since: 1.1.3 
	"""
	extension: Extension
	preThread: Runnable

	@overload
	def __init__(self, extension: Extension, runner: Core) -> None:
		pass

	@overload
	def trigger(self, macro: ScriptTrigger, event: BaseEvent, then: Runnable, catcher: Consumer) -> EventContainer:
		pass

	@overload
	def trigger(self, lang: str, script: str, fakeFile: File, event: BaseEvent, then: Runnable, catcher: Consumer) -> EventContainer:
		pass

	@overload
	def retrieveLibs(self, context: T) -> Mapping[str, BaseLibrary]:
		pass

	@overload
	def retrieveOnceLibs(self) -> Mapping[str, BaseLibrary]:
		pass

	@overload
	def retrievePerExecLibs(self, context: T) -> Mapping[str, BaseLibrary]:
		pass

	@overload
	def createContext(self, event: BaseEvent, file: File) -> T:
		pass

	pass


