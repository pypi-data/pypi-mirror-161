from __future__ import annotations

__all__ = ["app"]

import os
from typing import List, Dict

import asyncio
import aiofiles

from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from .models import Note
from .configuration import cfg, PATH, IMAGE_PATH, FRONT
from .versionning import gitRun, gitRemove, gitSave
from .authentication import get_current_user_from_token, init as auth_init

try:
    import orjson
except ImportError:
    app = FastAPI(debug=True)
else:
    from fastapi.responses import ORJSONResponse

    app = FastAPI(debug=True, default_response_class=ORJSONResponse)


@app.get("/")
def index():
    return RedirectResponse(url="/index.html")


@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user_from_token),
):
    fullname = os.path.join(IMAGE_PATH, file.filename)
    async with aiofiles.open(fullname, "wb") as f:
        await f.write(await file.read())


@app.delete("/notebook")
async def deleteNote(
    name: str, current_user: dict = Depends(get_current_user_from_token)
):
    """Remove one note"""
    await gitRemove(name)
    await gitSave(name, f"Removed {name}")


@app.post("/notebook")
async def addNote(
    note: Note, current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, str]:
    """Create one note"""
    assert "." not in note.name
    note.name = os.path.join(current_user["name"], note.name)
    assert not os.path.exists(note.filename)
    await note.save(creation=True)
    return dict(name=note.name)


@app.put("/notebook")
async def updateNote(
    note: Note, current_user: dict = Depends(get_current_user_from_token)
):
    """Update one note"""
    assert os.path.exists(note.filename)
    await note.save()


@app.get("/notebooks")
async def getNotes(
    current_user: dict = Depends(get_current_user_from_token),
) -> List[Note]:
    """Fetches the notebook"""
    entries = []
    for root, _dirs, files in os.walk(os.path.join(PATH, current_user["name"])):
        for file in files:
            if file.endswith(".md"):
                parent = root[len(PATH) :]
                doc = file[:-3]
                entries.append(await Note.load(os.path.join(parent, doc)))
    return entries


auth_init(app)
app.mount("/images/", StaticFiles(directory=IMAGE_PATH), name="images")
app.mount("/", StaticFiles(directory=FRONT), name="static")

if cfg["database"]["use_git"]:
    if not os.path.exists(os.path.join(PATH, ".git")):
        asyncio.gather(gitRun("init"))

    fullpath = os.path.abspath(os.path.expanduser(os.path.expandvars(PATH)))
    cwd = os.getcwd()
    os.chdir(PATH)
    for root, _dirs, files in os.walk(fullpath):
        for fname in files:
            if fname.endswith(".md"):
                os.system(f'git add "{root[len(fullpath)+1:]}/{fname}"')
    os.system('git commit -m "Wiki startup"')
    os.chdir(cwd)
