from sqlalchemy import Column, String
from src.core.models.base_model import Model


class Building(Model):
    __tablename__ = 'building'

    name = Column(String, nullable=True)
    building_url = Column(String, nullable=True)
    access_token = Column(String, nullable=True)

    def __repr__(self):
        return f"Building ({self.name=})"
