import contextlib
from src.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from typing import Any, AsyncIterator, Annotated
from fastapi import Depends
from src.logger import get_logger

logger = get_logger(__name__)


class DatabaseService:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        # Initialize the async engine with the provided host and additional arguments
        self._engine = create_async_engine(
            url=host,
            pool_pre_ping=True,
            pool_size=10,  # Increase the pool size
            max_overflow=20,  # Increase the overflow limit
            **engine_kwargs
        )

        # Create a session maker using the initialized engine
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            expire_on_commit=False,
        )

        # Register models
        self.register_models()

    @staticmethod
    def register_models():
        # Import and register all required models here
        from src.core.models.user_model import User
        from src.core.models.building import Building

    async def create_tables(self):
        # Create tables based on the metadata of the models
        async with self._engine.begin() as conn:
            from src.core.models.base_model import Model
            logger.info("[DATABASE]: Creating tables based on the metadata...")
            await conn.run_sync(Model.metadata.create_all, checkfirst=True)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._sessionmaker() as session:
            try:
                logger.debug("[DATABASE]: Yielding a new session")
                yield session
            except Exception as e:
                logger.error(f"[DATABASE]: DB Exception: {e}")
                await session.rollback()  # Rollback on exception
                raise
            finally:
                if session:
                    logger.debug("[DATABASE]: Closing session")
                    await session.close()
                    logger.debug("[DATABASE]: Session closed")

    async def close(self):
        # Properly dispose of the engine and clear session maker
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            logger.info("[DATABASE]: Database connection closed.")


# Initialize the database service with configuration settings
sessionmanager = DatabaseService(
    str(settings.DATABASE_URL),
    {"echo": settings.ECHO_SQL}
)


# Normal session to be used throughout
async def get_session() -> AsyncSession:
    async with sessionmanager.session() as session:
        return session


# Dependency function to be used in FastAPI routes
async def yield_db_session() -> AsyncIterator[AsyncSession]:
    async with sessionmanager.session() as session:
        yield session

# Annotated dependency for use within FastAPI routes
DBSession = Annotated[AsyncSession, Depends(yield_db_session)]
