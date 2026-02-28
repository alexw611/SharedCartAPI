from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import secrets

from API.database import get_db
from API.models.user import User
from API.models.group import Group
from API.models.user_group import UserGroup
from API.models.shopping_list import ShoppingList
from API.models.shopping_item import ShoppingItem
from API.schemas.group import GroupCreate, GroupUpdate, GroupResponse, GroupJoinRequest
from API.auth.dependencies import get_current_user
from API.rate_limiter import limiter

router = APIRouter(prefix="/groups", tags=["Groups"])


def generate_invite_code() -> str:
    """Generate a unique 8-character invite code."""
    return secrets.token_urlsafe(6)[:8].upper()


def get_group_member_names(group_id: int, db: Session) -> List[str]:
    """Get all members of a group with their display names."""
    user_groups = db.query(UserGroup).filter(UserGroup.groupId == group_id).all()
    user_ids = [ug.userId for ug in user_groups]
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    return [u.displayName for u in users]


def group_to_response(group: Group, db: Session) -> dict:
    """Convert group to response with members."""
    return {
        "id": group.id,
        "name": group.name,
        "note": group.note,
        "color": group.color,
        "inviteCode": group.inviteCode,
        "members": get_group_member_names(group.id, db)
    }


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def create_group(
    request: Request,
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new group and add current user as member."""
    new_group = Group(
        name=group_data.name,
        note=group_data.note,
        color=group_data.color,
        inviteCode=generate_invite_code()
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    user_group = UserGroup(userId=current_user.id, groupId=new_group.id)
    db.add(user_group)
    db.commit()
    
    return group_to_response(new_group, db)


@router.get("", response_model=List[GroupResponse])
@limiter.limit("120/minute")
def get_my_groups(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all groups the current user is a member of."""
    group_ids = db.query(UserGroup.groupId).filter(UserGroup.userId == current_user.id).all()
    group_ids = [g[0] for g in group_ids]
    
    groups = db.query(Group).filter(Group.id.in_(group_ids)).all()
    return [group_to_response(g, db) for g in groups]


@router.get("/{group_id}", response_model=GroupResponse)
@limiter.limit("120/minute")
def get_group(
    request: Request,
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific group."""
    membership = db.query(UserGroup).filter(
        UserGroup.userId == current_user.id,
        UserGroup.groupId == group_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    return group_to_response(group, db)


@router.put("/{group_id}", response_model=GroupResponse)
@limiter.limit("30/minute")
def update_group(
    request: Request,
    group_id: int,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a group."""
    membership = db.query(UserGroup).filter(
        UserGroup.userId == current_user.id,
        UserGroup.groupId == group_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    group.name = group_data.name
    group.note = group_data.note
    group.color = group_data.color
    db.commit()
    db.refresh(group)
    
    return group_to_response(group, db)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def delete_group(
    request: Request,
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a group."""
    membership = db.query(UserGroup).filter(
        UserGroup.userId == current_user.id,
        UserGroup.groupId == group_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    try:
        db.query(UserGroup).filter(UserGroup.groupId == group_id).delete(synchronize_session=False)
        list_ids_subq = db.query(ShoppingList.id).filter(ShoppingList.groupId == group_id).subquery()
        db.query(ShoppingItem).filter(ShoppingItem.shoppingListId.in_(list_ids_subq)).delete(synchronize_session=False)
        db.query(ShoppingList).filter(ShoppingList.groupId == group_id).delete(synchronize_session=False)
        db.delete(group)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/join", response_model=GroupResponse)
@limiter.limit("10/minute")
def join_group_by_code(
    request: Request,
    join_data: GroupJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a group using an invite code."""
    group = db.query(Group).filter(Group.inviteCode == join_data.inviteCode).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code"
        )
    
    existing = db.query(UserGroup).filter(
        UserGroup.userId == current_user.id,
        UserGroup.groupId == group.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this group"
        )
    
    new_member = UserGroup(userId=current_user.id, groupId=group.id)
    db.add(new_member)
    db.commit()
    
    return group_to_response(group, db)


@router.post("/{group_id}/regenerate-code", response_model=GroupResponse)
@limiter.limit("10/minute")
def regenerate_invite_code(
    request: Request,
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new invite code for the group."""
    membership = db.query(UserGroup).filter(
        UserGroup.userId == current_user.id,
        UserGroup.groupId == group_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    group.inviteCode = generate_invite_code()
    db.commit()
    db.refresh(group)
    
    return group_to_response(group, db)


@router.post("/{group_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def leave_group(
    request: Request,
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a group."""
    membership = db.query(UserGroup).filter(
        UserGroup.userId == current_user.id,
        UserGroup.groupId == group_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not a member of this group"
        )
    
    db.delete(membership)
    db.commit()


@router.post("/{group_id}/members/{user_id}", status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def add_member(
    request: Request,
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a user to a group."""
    membership = db.query(UserGroup).filter(
        UserGroup.userId == current_user.id,
        UserGroup.groupId == group_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    existing = db.query(UserGroup).filter(
        UserGroup.userId == user_id,
        UserGroup.groupId == group_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )
    
    new_member = UserGroup(userId=user_id, groupId=group_id)
    db.add(new_member)
    db.commit()
    
    return {"message": "Member added"}


@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def remove_member(
    request: Request,
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a user from a group."""
    membership = db.query(UserGroup).filter(
        UserGroup.userId == current_user.id,
        UserGroup.groupId == group_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    member = db.query(UserGroup).filter(
        UserGroup.userId == user_id,
        UserGroup.groupId == group_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member"
        )
    
    db.delete(member)
    db.commit()
