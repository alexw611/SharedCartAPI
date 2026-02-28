from sqlalchemy import Column, BigInteger, String, Text
from sqlalchemy.orm import relationship

from API.database import Base


class Group(Base):
    __tablename__ = "Groups"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    note = Column(Text, nullable=True)
    color = Column(String(50), nullable=True)
    inviteCode = Column(String(20), unique=True, nullable=True)
    
    users = relationship("UserGroup", back_populates="group")
    shoppingLists = relationship("ShoppingList", back_populates="group")
