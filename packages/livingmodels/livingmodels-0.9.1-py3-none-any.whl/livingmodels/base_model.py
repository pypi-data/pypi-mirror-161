from datetime import datetime

from sqlalchemy import (Column, Integer, DateTime)
from sqlalchemy.orm import registry

mapper_registry = registry()
Base = mapper_registry.generate_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
