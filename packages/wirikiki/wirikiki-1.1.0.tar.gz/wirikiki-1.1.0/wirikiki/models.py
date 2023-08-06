from __future__ import annotations

__all__ = ["Note"]

import os
from pydantic import BaseModel

import aiofiles

from .versionning import gitAdd, gitSave
from .configuration import PATH


class Note(BaseModel):
    "A markdown note"

    name: str
    content: str = ""

    @property
    def exists(self) -> bool:
        return os.path.exists(self.filename)

    @property
    def filename(self) -> str:
        return os.path.join(PATH, self.name) + ".md"

    @staticmethod
    async def load(name) -> Note:
        n = Note(name=name)
        async with aiofiles.open(n.filename, "r", encoding="utf-8") as f:
            n.content = await f.read()
        return n

    async def save(self, creation=False):
        if creation:  # auto make directory if it doesn't exist
            rootDir = os.path.dirname(self.filename)
            if not os.path.exists(rootDir):
                os.makedirs(rootDir, exist_ok=True)
        async with aiofiles.open(self.filename, "w", encoding="utf-8") as f:
            await f.write(self.content)
        if creation:
            await gitAdd(self.name)
        await gitSave(
            self.name,
            f"Udated {self.name}" if not creation else f"NEW note: {self.name}",
        )
