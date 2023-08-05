from typing import overload
from typing import TypeVar
from typing import Set
from typing import Generic
from .LibraryRegistry import LibraryRegistry
from .BaseEventRegistry import BaseEventRegistry
from .ExtensionLoader import ExtensionLoader
from .ConfigManager import ConfigManager
from .ServiceManager import ServiceManager
from .EventContainer import EventContainer
from .BaseScriptContext import BaseScriptContext
from .ScriptTrigger import ScriptTrigger
from .BaseEvent import BaseEvent
from .BaseWrappedException import BaseWrappedException

Function = TypeVar["java.util.function.Function_xyz.wagyourtail.jsmacros.core.Core_V,R_,R_"]
T = TypeVar("T")
Consumer = TypeVar["java.util.function.Consumer_java.lang.Throwable_"]
U = TypeVar("U")
BiFunction = TypeVar["java.util.function.BiFunction_xyz.wagyourtail.jsmacros.core.Core_V,R_,org.slf4j.Logger,V_"]
Runnable = TypeVar["java.lang.Runnable"]
Throwable = TypeVar["java.lang.Throwable"]
Logger = TypeVar["org.slf4j.Logger"]
File = TypeVar["java.io.File"]

class Core(Generic[T, U]):
	libraryRegistry: LibraryRegistry
	eventRegistry: BaseEventRegistry
	extensions: ExtensionLoader
	profile: T
	config: ConfigManager
	services: ServiceManager

	@overload
	def getInstance(self) -> "Core":
		"""static reference to instance created by Core#<V,R>createInstance(java.util.function.Function<xyz.wagyourtail.jsmacros.core.Core<V,R>,R>,java.util.function.BiFunction<xyz.wagyourtail.jsmacros.core.Core<V,R>,org.slf4j.Logger,V>,java.io.File,java.io.File,org.slf4j.Logger)
		"""
		pass

	@overload
	def deferredInit(self) -> None:
		pass

	@overload
	def addContext(self, container: EventContainer) -> None:
		"""

		Args:
			container: 
		"""
		pass

	@overload
	def getContexts(self) -> Set[BaseScriptContext]:
		"""
		"""
		pass

	@overload
	def createInstance(self, eventRegistryFunction: Function, profileFunction: BiFunction, configFolder: File, macroFolder: File, logger: Logger) -> "Core":
		"""start by running this function, supplying implementations of BaseEventRegistry and BaseProfile and a Supplier for
creating the config manager with the folder paths it needs.

		Args:
			eventRegistryFunction: 
			logger: 
			macroFolder: 
			profileFunction: 
			configFolder: 
		"""
		pass

	@overload
	def exec(self, macro: ScriptTrigger, event: BaseEvent) -> EventContainer:
		"""executes an BaseEvent on a $ ScriptTrigger

		Args:
			macro: 
			event: 
		"""
		pass

	@overload
	def exec(self, macro: ScriptTrigger, event: BaseEvent, then: Runnable, catcher: Consumer) -> EventContainer:
		"""Executes an BaseEvent on a $ ScriptTrigger with callback.

		Args:
			macro: 
			catcher: 
			then: 
			event: 
		"""
		pass

	@overload
	def exec(self, lang: str, script: str, fakeFile: File, event: BaseEvent, then: Runnable, catcher: Consumer) -> EventContainer:
		"""
		Since: 1.7.0 

		Args:
			catcher: 
			fakeFile: 
			then: 
			lang: 
			event: 
			script: 
		"""
		pass

	@overload
	def wrapException(self, ex: Throwable) -> BaseWrappedException:
		"""wraps an exception for more uniform parsing between languages, also extracts useful info.

		Args:
			ex: exception to wrap. 
		"""
		pass

	pass


