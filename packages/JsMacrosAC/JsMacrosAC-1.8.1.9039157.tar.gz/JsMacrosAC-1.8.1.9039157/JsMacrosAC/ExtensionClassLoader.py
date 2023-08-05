from typing import overload
from typing import List


class ExtensionClassLoader(URLClassLoader):

	@overload
	def __init__(self, urls: List[URL]) -> None:
		pass

	@overload
	def addURL(self, url: URL) -> None:
		pass

	pass


