from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from API.database import get_db
from API.auth.dependencies import get_current_user
from API.models.user import User
from API.models.group import Group
from API.models.user_group import UserGroup
from API.models.shopping_list import ShoppingList
from API.models.shopping_item import ShoppingItem
from API.schemas.snapshot import Snapshot, GroupSnapshot
from API.rate_limiter import limiter

router = APIRouter(prefix="/snapshot", tags=["Snapshot"])


def get_group_member_names(group_id: int, db: Session) -> list:
    """Get display names of all group members."""
    user_groups = db.query(UserGroup).filter(UserGroup.groupId == group_id).all()
    user_ids = [ug.userId for ug in user_groups]
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    return [u.displayName for u in users]


@router.get("", response_model=Snapshot)
@limiter.limit("70/minute")
def get_snapshot(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all data for current user in one request."""
    
    user_groups = db.query(UserGroup).filter(
        UserGroup.userId == current_user.id
    ).all()
    
    group_ids = [ug.groupId for ug in user_groups]
    
    groups = db.query(Group).filter(
        Group.id.in_(group_ids)
    ).all()
    
    groups_with_members = [
        GroupSnapshot(
            id=g.id,
            name=g.name,
            note=g.note,
            color=g.color,
            inviteCode=g.inviteCode,
            members=get_group_member_names(g.id, db)
        )
        for g in groups
    ]
    
    shopping_lists = db.query(ShoppingList).filter(
        ShoppingList.groupId.in_(group_ids)
    ).all()
    
    list_ids = [sl.id for sl in shopping_lists]
    
    shopping_items = db.query(ShoppingItem).filter(
        ShoppingItem.shoppingListId.in_(list_ids)
    ).all()
    
    return Snapshot(
        user=current_user,
        groups=groups_with_members,
        userGroups=user_groups,
        shoppingLists=shopping_lists,
        shoppingItems=shopping_items
    )
