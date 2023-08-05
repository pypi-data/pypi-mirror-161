from typing import overload
from .History_HistoryStep import History_HistoryStep
from .SelectCursor import SelectCursor


class History_TabLinesKeepCursor(History_HistoryStep):

	@overload
	def __init__(self, startLine: int, startLineIndex: int, endLineIndex: int, lineCount: int, reversed: bool, cursor: SelectCursor) -> None:
		pass

	pass


