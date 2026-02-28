from sqlalchemy import Column, BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from API.database import Base


class ShoppingList(Base):
    __tablename__ = "ShoppingLists"
    
    id = Column(BigInteger, primary_key=True, index=True)
    groupId = Column(BigInteger, ForeignKey("Groups.id"), nullable=False)
    name = Column(String(255), nullable=False)
    note = Column(Text, nullable=True)
    
    group = relationship("Group", back_populates="shoppingLists")
    items = relationship("ShoppingItem", back_populates="shoppingList")
