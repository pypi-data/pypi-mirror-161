import hashlib

from typing import Optional, Dict
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime
from jose import JWTError, jwt  # type: ignore

from .configuration import cfg, USERS


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    data_copy = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=cfg["token"]["expire_minutes"])
    )
    data_copy.update({"exp": expire})
    return jwt.encode(
        data_copy, cfg["token"]["key"], algorithm=cfg["token"]["algorithm"]
    )


_user_db: Dict[str, str] = {}


def get_user_db() -> Dict[str, str]:
    if not _user_db:
        for line in open(USERS, "r", encoding="utf-8"):
            user, password = line.split(" ", 1)
            _user_db[user] = password.strip()
    return _user_db


class Token(BaseModel):
    access_token: str
    token_type: str


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: dict = Depends(get_user_db)
) -> Dict[str, str]:
    try:
        payload = jwt.decode(
            token, cfg["token"]["key"], algorithms=[cfg["token"]["algorithm"]]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if not (cfg["users"]["allow_anonymous"] and username == "anonymous"):
        user = db.get(username)
        if user is None:
            raise credentials_exception
    return dict(name=username)


def make_password(password: str) -> str:
    text = (cfg["users"]["salt"] + password).encode("utf-8")
    return hashlib.sha512(text).hexdigest()


def init(application):
    @application.post("/token", response_model=Token)
    def _login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: dict = Depends(get_user_db),
    ) -> Dict[str, str]:
        is_anonymous = (
            form_data.username == "anonymous" and cfg["users"]["allow_anonymous"]
        )
        if is_anonymous or (
            make_password(form_data.password) == db.get(form_data.username)
        ):
            access_token = create_access_token(
                data={"sub": form_data.username},
            )
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise credentials_exception
