from pydantic import BaseModel
from typing import Optional


class ShoppingListBase(BaseModel):
    name: str
    note: Optional[str] = None


class ShoppingListCreate(ShoppingListBase):
    groupId: int


class ShoppingListUpdate(ShoppingListBase):
    pass


class ShoppingListResponse(ShoppingListBase):
    id: int
    groupId: int
    
    class Config:
        from_attributes = True
