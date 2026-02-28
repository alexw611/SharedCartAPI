from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class ShoppingItemBase(BaseModel):
    name: str
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    note: Optional[str] = None


class ShoppingItemCreate(ShoppingItemBase):
    shoppingListId: int


class ShoppingItemUpdate(ShoppingItemBase):
    pass


class ShoppingItemResponse(ShoppingItemBase):
    id: int
    shoppingListId: int
    checked: bool = False
    
    class Config:
        from_attributes = True
