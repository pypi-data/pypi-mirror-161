from typing import overload
from typing import TypeVar

Entity = TypeVar["net.minecraft.entity.Entity"]
CallbackInfoReturnable = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable_net.minecraft.util.ActionResult_"]
CallbackInfo = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfo"]
BlockPos = TypeVar["net.minecraft.util.math.BlockPos"]
ClientPlayerEntity = TypeVar["net.minecraft.client.network.ClientPlayerEntity"]
BlockHitResult = TypeVar["net.minecraft.util.hit.BlockHitResult"]
Hand = TypeVar["net.minecraft.util.Hand"]
Direction = TypeVar["net.minecraft.util.math.Direction"]
PlayerEntity = TypeVar["net.minecraft.entity.player.PlayerEntity"]

class MixinClientPlayerInteractionManager:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def onInteractBlock(self, player: ClientPlayerEntity, hand: Hand, hitResult: BlockHitResult, cir: CallbackInfoReturnable) -> None:
		pass

	@overload
	def onAttackBlock(self, pos: BlockPos, direction: Direction, cir: CallbackInfoReturnable) -> None:
		pass

	@overload
	def onAttackEntity(self, player: PlayerEntity, target: Entity, ci: CallbackInfo) -> None:
		pass

	@overload
	def onInteractEntity(self, player: PlayerEntity, entity: Entity, hand: Hand, cir: CallbackInfoReturnable) -> None:
		pass

	pass


