from typing import Any, Protocol
from sqlalchemy.orm.session import Session


class IRepoContext(Protocol):
    session: Session

    def __enter__(self) -> "IRepoContext": ...

    def __exit__(self, *args: Any): ...
