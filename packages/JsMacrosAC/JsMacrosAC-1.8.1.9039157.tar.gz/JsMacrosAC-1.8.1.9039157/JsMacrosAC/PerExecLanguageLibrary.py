from typing import overload
from typing import TypeVar
from typing import Generic
from .BaseLibrary import BaseLibrary

T = TypeVar("T")
U = TypeVar("U")

class PerExecLanguageLibrary(Generic[U, T], BaseLibrary):

	@overload
	def __init__(self, context: T, language: Class) -> None:
		pass

	pass


