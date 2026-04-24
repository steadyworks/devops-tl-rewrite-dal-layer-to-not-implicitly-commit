from typing import TYPE_CHECKING, AsyncGenerator, Callable

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from backend.app import TimelensApp  # Avoids actual circular import


class RouteHandler:
    def __init__(self, app: "TimelensApp") -> None:
        self.app = app
        self.router = APIRouter()
        self.get_session: Callable[[], AsyncGenerator[AsyncSession, None]] = (
            app.get_db_session_dependency()
        )
        self.register_routes()

    def register_routes(self) -> None:
        pass

    def get_router(self) -> APIRouter:
        return self.router
