from typing import overload


class IClientPlayerEntity:

	@overload
	def jsmacros_sendChatMessageBypass(self, message: str) -> None:
		pass

	pass


