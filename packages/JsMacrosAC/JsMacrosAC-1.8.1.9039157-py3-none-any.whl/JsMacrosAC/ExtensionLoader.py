from typing import overload
from typing import TypeVar
from typing import Set
from .Core import Core
from .Extension import Extension

File = TypeVar["java.io.File"]

class ExtensionLoader:

	@overload
	def __init__(self, core: Core) -> None:
		pass

	@overload
	def isExtensionLoaded(self, name: str) -> bool:
		pass

	@overload
	def notLoaded(self) -> bool:
		pass

	@overload
	def getHighestPriorityExtension(self) -> Extension:
		pass

	@overload
	def getAllExtensions(self) -> Set[Extension]:
		pass

	@overload
	def getExtensionForFile(self, file: File) -> Extension:
		pass

	@overload
	def getExtensionForName(self, lang: str) -> Extension:
		pass

	@overload
	def loadExtensions(self) -> None:
		pass

	@overload
	def isGuestObject(self, obj: object) -> bool:
		pass

	pass


