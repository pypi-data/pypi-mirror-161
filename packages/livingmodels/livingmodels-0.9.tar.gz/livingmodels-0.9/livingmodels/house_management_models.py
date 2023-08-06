from sqlalchemy import (Column, String)
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class HouseManagementCompany(BaseModel):
    """  Справочник упарввляющихх компаний"""

    __tablename__ = 'house_management_company'
    __table_args__ = {"extend_existing": True}

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    estate_complexes = relationship('EstateComplexes', back_populates='house_management_company', uselist=True)
