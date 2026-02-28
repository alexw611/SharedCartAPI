from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class UserSnapshot(BaseModel):
    id: int
    username: str
    displayName: str
    
    class Config:
        from_attributes = True


class GroupSnapshot(BaseModel):
    id: int
    name: str
    note: Optional[str] = None
    color: Optional[str] = None
    inviteCode: Optional[str] = None
    members: List[str] = []
    
    class Config:
        from_attributes = True


class UserGroupSnapshot(BaseModel):
    userId: int
    groupId: int
    
    class Config:
        from_attributes = True


class ShoppingListSnapshot(BaseModel):
    id: int
    groupId: int
    name: str
    note: Optional[str] = None
    
    class Config:
        from_attributes = True


class ShoppingItemSnapshot(BaseModel):
    id: int
    shoppingListId: int
    name: str
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    note: Optional[str] = None
    checked: bool = False
    
    class Config:
        from_attributes = True


class Snapshot(BaseModel):
    user: UserSnapshot
    groups: List[GroupSnapshot]
    userGroups: List[UserGroupSnapshot]
    shoppingLists: List[ShoppingListSnapshot]
    shoppingItems: List[ShoppingItemSnapshot]
