from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from API.database import Base


class User(Base):
    __tablename__ = "Users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    displayName = Column(String(255), nullable=False)
    passwordHash = Column(String(255), nullable=False)
    
    groups = relationship("UserGroup", back_populates="user", cascade="all, delete-orphan")
