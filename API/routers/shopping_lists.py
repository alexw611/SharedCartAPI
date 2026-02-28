from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from API.database import get_db
from API.models.user import User
from API.models.user_group import UserGroup
from API.models.shopping_list import ShoppingList
from API.models.shopping_item import ShoppingItem
from API.schemas.shopping_list import ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse
from API.auth.dependencies import get_current_user

router = APIRouter(prefix="/lists", tags=["Shopping Lists"])


def check_group_access(user_id: int, group_id: int, db: Session):
    """Check if user has access to group."""
    membership = db.query(UserGroup).filter(
        UserGroup.userId == user_id,
        UserGroup.groupId == group_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this group"
        )


@router.post("", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: ShoppingListCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new shopping list."""
    check_group_access(current_user.id, list_data.groupId, db)
    
    new_list = ShoppingList(
        groupId=list_data.groupId,
        name=list_data.name,
        note=list_data.note
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    
    return new_list


@router.get("", response_model=List[ShoppingListResponse])
def get_my_lists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all shopping lists from user's groups."""
    # Get user's groups
    group_ids = db.query(UserGroup.groupId).filter(UserGroup.userId == current_user.id).all()
    group_ids = [g[0] for g in group_ids]
    
    # Get lists from those groups
    lists = db.query(ShoppingList).filter(ShoppingList.groupId.in_(group_ids)).all()
    return lists


@router.get("/{list_id}", response_model=ShoppingListResponse)
def get_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific shopping list."""
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    
    check_group_access(current_user.id, shopping_list.groupId, db)
    
    return shopping_list


@router.put("/{list_id}", response_model=ShoppingListResponse)
def update_list(
    list_id: int,
    list_data: ShoppingListUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a shopping list."""
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    
    check_group_access(current_user.id, shopping_list.groupId, db)
    
    shopping_list.name = list_data.name
    shopping_list.note = list_data.note
    db.commit()
    db.refresh(shopping_list)
    
    return shopping_list


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a shopping list."""
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    
    check_group_access(current_user.id, shopping_list.groupId, db)
    
    # Manually delete items first to avoid IntegrityError (NOT NULL constraint)
    db.query(ShoppingItem).filter(ShoppingItem.shoppingListId == list_id).delete(synchronize_session=False)
    
    db.delete(shopping_list)
    db.commit()
