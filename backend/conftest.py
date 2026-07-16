"""Pytest fixtures for CondoCombat backend tests."""

import os

# Define SECRET_KEY before any project import to ensure settings picks it up
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-32chars-min!")

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_session():
    """Mock de AsyncSession para testes unitários de repository.

    Retorna AsyncMock para métodos async (commit, flush, etc.)
    e MagicMock para o Result de execute(), garantindo que métodos
    sync como scalar_one_or_none() e scalars().all() funcionem.
    """
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    scalars_mock = MagicMock()
    scalars_mock.all = MagicMock(return_value=[])
    result.scalars = MagicMock(return_value=scalars_mock)
    session.execute = AsyncMock(return_value=result)
    session.add = MagicMock()
    session.add_all = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.close = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
async def async_session():
    """Sessão async real contra SQLite em memória, para testes de ORM.

    Cria o schema a partir do Base.metadata a cada teste, garantindo
    isolamento entre eles.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app import models  # noqa: F401 — importa os modelos para popular Base.metadata
    from app.database import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session

    await engine.dispose()
