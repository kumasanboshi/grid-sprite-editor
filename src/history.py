from PIL import Image


class HistoryManager:
    """Undo/Redo manager. Stores PIL Image snapshots."""

    MAX_STEPS = 50

    def __init__(self):
        self._undo_stack: list[Image.Image] = []
        self._redo_stack: list[Image.Image] = []

    def push(self, image: Image.Image):
        """Call before every edit operation."""
        self._undo_stack.append(image.copy())
        if len(self._undo_stack) > self.MAX_STEPS:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self, current: Image.Image) -> Image.Image | None:
        if not self._undo_stack:
            return None
        self._redo_stack.append(current.copy())
        return self._undo_stack.pop()

    def redo(self, current: Image.Image) -> Image.Image | None:
        if not self._redo_stack:
            return None
        self._undo_stack.append(current.copy())
        return self._redo_stack.pop()

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
