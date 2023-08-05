from typing import overload
from typing import TypeVar
from .IClientPlayerEntity import IClientPlayerEntity

GameProfile = TypeVar["com.mojang.authlib.GameProfile"]
AbstractClientPlayerEntity = TypeVar["net.minecraft.client.network.AbstractClientPlayerEntity"]
ClientWorld = TypeVar["net.minecraft.client.world.ClientWorld"]

class MixinClientPlayerEntity(IClientPlayerEntity, AbstractClientPlayerEntity):

	@overload
	def __init__(self, world: ClientWorld, profile: GameProfile, publicKey: PlayerPublicKey) -> None:
		pass

	@overload
	def jsmacros_sendChatMessageBypass(self, message: str) -> None:
		pass

	pass


