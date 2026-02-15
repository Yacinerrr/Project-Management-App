from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from .. import models, schemas
from .. import auth as auth_utils
from ..database import get_db

router = APIRouter(prefix="/columns", tags=["Columns"])

def check_board_access(board_id: str, user_id: str, db: Session):
    """Helper function to check if user has access to a board"""
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == board.project_id,
        models.ProjectMember.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this board"
        )
    
    return board

@router.post("", response_model=schemas.BoardColumn, status_code=status.HTTP_201_CREATED)
def create_column(
    column: schemas.BoardColumnCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Create a new column in a board"""
    # Check board access
    check_board_access(column.board_id, current_user.id, db)
    
    # Create the column
    new_column = models.BoardColumn(
        id=str(uuid.uuid4()),
        name=column.name,
        board_id=column.board_id,
        position=column.position
    )
    
    db.add(new_column)
    db.commit()
    db.refresh(new_column)
    
    return new_column

@router.get("/board/{board_id}", response_model=List[schemas.BoardColumn])
def get_board_columns(
    board_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get all columns for a board"""
    # Check board access
    check_board_access(board_id, current_user.id, db)
    
    # Get all columns ordered by position
    columns = db.query(models.BoardColumn).filter(
        models.BoardColumn.board_id == board_id
    ).order_by(models.BoardColumn.position).all()
    
    return columns

@router.get("/{column_id}", response_model=schemas.BoardColumn)
def get_column(
    column_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get a specific column"""
    column = db.query(models.BoardColumn).filter(models.BoardColumn.id == column_id).first()
    
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Check board access
    check_board_access(column.board_id, current_user.id, db)
    
    return column

@router.put("/{column_id}", response_model=schemas.BoardColumn)
def update_column(
    column_id: str,
    column_update: schemas.BoardColumnBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Update a column"""
    column = db.query(models.BoardColumn).filter(models.BoardColumn.id == column_id).first()
    
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Check board access
    check_board_access(column.board_id, current_user.id, db)
    
    # Update column
    column.name = column_update.name
    column.position = column_update.position
    
    db.commit()
    db.refresh(column)
    
    return column

@router.delete("/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_column(
    column_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Delete a column"""
    column = db.query(models.BoardColumn).filter(models.BoardColumn.id == column_id).first()
    
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Check board access
    check_board_access(column.board_id, current_user.id, db)
    
    db.delete(column)
    db.commit()
    
    return None