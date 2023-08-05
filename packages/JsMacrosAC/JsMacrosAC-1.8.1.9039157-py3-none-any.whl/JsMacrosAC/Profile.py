from typing import overload
from typing import List
from typing import TypeVar
from .BaseProfile import BaseProfile
from .Core import Core
from .BaseEvent import BaseEvent

Throwable = TypeVar["java.lang.Throwable"]
Logger = TypeVar["org.slf4j.Logger"]

class Profile(BaseProfile):
	ignoredErrors: List[Class]

	@overload
	def __init__(self, runner: Core, logger: Logger) -> None:
		pass

	@overload
	def triggerEventJoin(self, event: BaseEvent) -> None:
		pass

	@overload
	def triggerEventJoinNoAnything(self, event: BaseEvent) -> None:
		pass

	@overload
	def logError(self, ex: Throwable) -> None:
		pass

	@overload
	def checkJoinedThreadStack(self) -> bool:
		pass

	@overload
	def initRegistries(self) -> None:
		pass

	pass


