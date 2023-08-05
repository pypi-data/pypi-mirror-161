from typing import overload
from typing import List
from typing import TypeVar
from .BaseHelper import BaseHelper
from .BlockStateHelper import BlockStateHelper
from .ItemStackHelper import ItemStackHelper

Block = TypeVar["net.minecraft.block.Block"]

class BlockHelper(BaseHelper):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, base: Block) -> None:
		pass

	@overload
	def getDefaultState(self) -> BlockStateHelper:
		"""
		Since: 1.6.5 

		Returns:
			the default state of the block. 
		"""
		pass

	@overload
	def getDefaultItemStack(self) -> ItemStackHelper:
		"""
		Since: 1.6.5 

		Returns:
			the default item stack of the block. 
		"""
		pass

	@overload
	def canMobSpawnInside(self) -> bool:
		pass

	@overload
	def hasDynamicBounds(self) -> bool:
		"""
		Since: 1.6.5 

		Returns:
			'true' if the block has dynamic bounds. 
		"""
		pass

	@overload
	def getBlastResistance(self) -> float:
		"""
		Since: 1.6.5 

		Returns:
			the blast resistance. 
		"""
		pass

	@overload
	def getJumpVelocityMultiplier(self) -> float:
		"""
		Since: 1.6.5 

		Returns:
			the jump velocity multiplier. 
		"""
		pass

	@overload
	def getSlipperiness(self) -> float:
		"""
		Since: 1.6.5 

		Returns:
			the slipperiness. 
		"""
		pass

	@overload
	def getHardness(self) -> float:
		"""
		Since: 1.6.5 

		Returns:
			the hardness. 
		"""
		pass

	@overload
	def getVelocityMultiplier(self) -> float:
		"""
		Since: 1.6.5 

		Returns:
			the velocity multiplier. 
		"""
		pass

	@overload
	def getTags(self) -> List[str]:
		"""
		Since: 1.6.5 

		Returns:
			all tags of the block as an ArrayList . 
		"""
		pass

	@overload
	def getStates(self) -> List[BlockStateHelper]:
		"""
		Since: 1.6.5 

		Returns:
			all possible block states of the block. 
		"""
		pass

	@overload
	def getId(self) -> str:
		"""
		Since: 1.6.5 

		Returns:
			the identifier of the block. 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


