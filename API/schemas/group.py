from pydantic import BaseModel
from typing import Optional, List


class GroupBase(BaseModel):
    name: str
    note: Optional[str] = None
    color: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    pass


class GroupResponse(GroupBase):
    id: int
    inviteCode: Optional[str] = None
    members: List[str] = []
    
    class Config:
        from_attributes = True


class GroupJoinRequest(BaseModel):
    inviteCode: str
