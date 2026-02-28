from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from API.database import get_db
from API.models.user import User
from API.models.user_group import UserGroup
from API.models.shopping_list import ShoppingList
from API.models.shopping_item import ShoppingItem
from API.schemas.shopping_item import ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse
from API.auth.dependencies import get_current_user

router = APIRouter(prefix="/items", tags=["Shopping Items"])


def check_list_access(user_id: int, list_id: int, db: Session) -> ShoppingList:
    """Check if user has access to list and return it."""
    shopping_list = db.query(ShoppingList).filter(ShoppingList.id == list_id).first()
    
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    
    membership = db.query(UserGroup).filter(
        UserGroup.userId == user_id,
        UserGroup.groupId == shopping_list.groupId
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this list"
        )
    
    return shopping_list


def check_item_access(user_id: int, item_id: int, db: Session) -> ShoppingItem:
    """Check if user has access to item and return it."""
    item = db.query(ShoppingItem).filter(ShoppingItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    check_list_access(user_id, item.shoppingListId, db)
    
    return item


@router.post("", response_model=ShoppingItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: ShoppingItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an item to a shopping list."""
    check_list_access(current_user.id, item_data.shoppingListId, db)
    
    new_item = ShoppingItem(
        shoppingListId=item_data.shoppingListId,
        name=item_data.name,
        quantity=item_data.quantity,
        unit=item_data.unit,
        note=item_data.note
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item


@router.get("/list/{list_id}", response_model=List[ShoppingItemResponse])
def get_items_by_list(
    list_id: int,
    sort_by: Optional[str] = Query(None, regex="^(name|checked)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    checked: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all items from a shopping list with optional sorting and filtering."""
    check_list_access(current_user.id, list_id, db)
    
    query = db.query(ShoppingItem).filter(ShoppingItem.shoppingListId == list_id)
    
    # Filter by checked status
    if checked is not None:
        query = query.filter(ShoppingItem.checked == checked)
    
    # Sorting
    if sort_by == "name":
        if sort_order == "desc":
            query = query.order_by(ShoppingItem.name.desc())
        else:
            query = query.order_by(ShoppingItem.name.asc())
    elif sort_by == "checked":
        if sort_order == "desc":
            query = query.order_by(ShoppingItem.checked.desc())
        else:
            query = query.order_by(ShoppingItem.checked.asc())
    
    items = query.all()
    return items


@router.get("/{item_id}", response_model=ShoppingItemResponse)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific item."""
    item = check_item_access(current_user.id, item_id, db)
    return item


@router.put("/{item_id}", response_model=ShoppingItemResponse)
def update_item(
    item_id: int,
    item_data: ShoppingItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an item."""
    item = check_item_access(current_user.id, item_id, db)
    
    item.name = item_data.name
    item.quantity = item_data.quantity
    item.unit = item_data.unit
    item.note = item_data.note
    db.commit()
    db.refresh(item)
    
    return item


@router.patch("/{item_id}/check", response_model=ShoppingItemResponse)
def toggle_item_checked(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle item checked status."""
    item = check_item_access(current_user.id, item_id, db)
    
    item.checked = not item.checked
    db.commit()
    db.refresh(item)
    
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an item."""
    item = check_item_access(current_user.id, item_id, db)
    
    db.delete(item)
    db.commit()
