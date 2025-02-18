from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, func, DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from src.constants import DB_NAMING_CONVENTION
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base


@as_declarative()
class BaseModel:
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        instance = cls(**kwargs)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @classmethod
    async def get(cls, db: AsyncSession, id: int):
        try:
            instance = await db.get(cls, id)
        except NoResultFound:
            return None
        return instance

    @classmethod
    async def update(cls, db: AsyncSession, id: int, **kwargs):
        try:
            instance = await db.get(cls, id)
        except NoResultFound:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await db.merge(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @classmethod
    async def delete(cls, db: AsyncSession, id: int):
        try:
            instance = await db.get(cls, id)
        except NoResultFound:
            return False
        await db.delete(instance)
        await db.commit()
        return True

    @classmethod
    async def list(cls, db: AsyncSession):
        result = await db.execute(select(cls))
        return result.scalars().all()

    @classmethod
    async def filter_by(cls, db: AsyncSession, **kwargs):
        query = select(cls)
        for key, value in kwargs.items():
            query = query.where(getattr(cls, key) == value)
        result = await db.execute(query)
        return result.scalars().first()

    @property
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_sa')}

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
Model = declarative_base(cls=BaseModel, metadata=metadata, name="Model")
