from sqlalchemy import Column, Integer, String
from db import Base

class InternalDoc(Base):
    __tablename__ = "internal_docs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
