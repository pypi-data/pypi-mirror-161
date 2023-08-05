from typing import overload


class Util:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def tryAutoCastNumber(self, returnType: Class, number: object) -> object:
		pass

	pass


