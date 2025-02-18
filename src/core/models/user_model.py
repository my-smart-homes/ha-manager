from sqlalchemy import Column, String
from src.core.models.base_model import Model


class User(Model):
    __tablename__ = 'user'

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    dob = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip = Column(String, nullable=True)
    email = Column(String, nullable=True)
    cell_phone = Column(String, nullable=True)
    contacting_number = Column(String, nullable=True)

    def __repr__(self):
        return f"User({self.id=}, {self.contacting_number=}, {self.email=})"
