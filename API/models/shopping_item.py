from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from API.database import Base


class ShoppingItem(Base):
    __tablename__ = "ShoppingItems"
    
    id = Column(BigInteger, primary_key=True, index=True)
    shoppingListId = Column(BigInteger, ForeignKey("ShoppingLists.id"), nullable=False)
    name = Column(String(255), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=True)
    unit = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    checked = Column(Boolean, default=False, nullable=False)
    
    shoppingList = relationship("ShoppingList", back_populates="items")
