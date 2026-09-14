from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from global_src.constants import DATABASE_PATH


class Database:
    def __init__(self, path: str | Path = DATABASE_PATH, echo: bool = False) -> None:
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine: AsyncEngine = create_async_engine(
            f"sqlite+aiosqlite:///{self.path.as_posix()}",
            echo=echo,
        )
        self.session_factory = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            yield session

    async def initialize(self) -> None:
        from global_src import models

        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
            for trigger in models.TRIGGERS:
                await conn.exec_driver_sql(trigger)

    async def close(self) -> None:
        await self.engine.dispose()


DATABASE = Database()
