from typing import overload
from typing import TypeVar
from typing import Set

KeyBinding = TypeVar["net.minecraft.client.option.KeyBinding"]
InputUtil_Key = TypeVar["net.minecraft.client.util.InputUtil.Key"]

class FKeyBind_KeyTracker:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def press(self, key: InputUtil_Key) -> None:
		pass

	@overload
	def press(self, bind: KeyBinding) -> None:
		pass

	@overload
	def unpress(self, key: InputUtil_Key) -> None:
		pass

	@overload
	def unpress(self, bind: KeyBinding) -> None:
		pass

	@overload
	def getPressedKeys(self) -> Set[str]:
		pass

	pass


