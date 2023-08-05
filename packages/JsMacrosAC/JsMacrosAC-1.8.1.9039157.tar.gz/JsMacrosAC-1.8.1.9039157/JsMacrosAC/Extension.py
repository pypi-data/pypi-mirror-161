from typing import overload
from typing import TypeVar
from typing import Mapping
from typing import Set
from .Extension_ExtMatch import Extension_ExtMatch
from .Core import Core
from .BaseLanguage import BaseLanguage
from .BaseWrappedException import BaseWrappedException

Throwable = TypeVar["java.lang.Throwable"]
File = TypeVar["java.io.File"]

class Extension:

	@overload
	def init(self) -> None:
		pass

	@overload
	def getPriority(self) -> int:
		pass

	@overload
	def getLanguageImplName(self) -> str:
		pass

	@overload
	def extensionMatch(self, file: File) -> Extension_ExtMatch:
		pass

	@overload
	def defaultFileExtension(self) -> str:
		pass

	@overload
	def getLanguage(self, runner: Core) -> BaseLanguage:
		"""

		Returns:
			a single static instance of the language definition 
		"""
		pass

	@overload
	def getLibraries(self) -> Set[Class]:
		pass

	@overload
	def getDependencies(self) -> Set[URL]:
		pass

	@overload
	def getDependenciesInternal(self, clazz: Class, fname: str) -> Set[URL]:
		pass

	@overload
	def wrapException(self, t: Throwable) -> BaseWrappedException:
		pass

	@overload
	def getTranslations(self, lang: str) -> Mapping[str, str]:
		pass

	@overload
	def getTranslationsInternal(self, clazz: Class, fname: str) -> Mapping[str, str]:
		pass

	@overload
	def isGuestObject(self, o: object) -> bool:
		pass

	pass


