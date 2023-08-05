from typing import overload
from typing import TypeVar

T = TypeVar("T")

class MixinSimpleOption:

	@overload
	def forceSetValue(self, value: T) -> None:
		pass

	pass


