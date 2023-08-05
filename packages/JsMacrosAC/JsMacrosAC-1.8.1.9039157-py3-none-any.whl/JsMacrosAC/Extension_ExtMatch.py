from typing import overload
from typing import List


class Extension_ExtMatch:
	NOT_MATCH: "Extension_ExtMatch"
	MATCH: "Extension_ExtMatch"
	MATCH_WITH_NAME: "Extension_ExtMatch"

	@overload
	def values(self) -> List["Extension_ExtMatch"]:
		pass

	@overload
	def valueOf(self, name: str) -> "Extension_ExtMatch":
		pass

	@overload
	def isMatch(self) -> bool:
		pass

	pass


