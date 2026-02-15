from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from .. import models, schemas
from .. import auth as auth_utils
from ..database import get_db

router = APIRouter(prefix="/boards", tags=["Boards"])

def check_project_access(project_id: str, user_id: str, db: Session):
    """Helper function to check if user has access to a project"""
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )
    return membership

@router.post("", response_model=schemas.Board, status_code=status.HTTP_201_CREATED)
def create_board(
    board: schemas.BoardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Create a new board in a project"""
    # Check project access
    check_project_access(board.project_id, current_user.id, db)
    
    # Create the board
    new_board = models.Board(
        id=str(uuid.uuid4()),
        name=board.name,
        project_id=board.project_id,
        position=board.position
    )
    
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    
    return new_board

@router.get("/project/{project_id}", response_model=List[schemas.Board])
def get_project_boards(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get all boards for a project"""
    # Check project access
    check_project_access(project_id, current_user.id, db)
    
    # Get all boards ordered by position
    boards = db.query(models.Board).filter(
        models.Board.project_id == project_id
    ).order_by(models.Board.position).all()
    
    return boards

@router.get("/{board_id}", response_model=schemas.Board)
def get_board(
    board_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get a specific board"""
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check project access
    check_project_access(board.project_id, current_user.id, db)
    
    return board

@router.put("/{board_id}", response_model=schemas.Board)
def update_board(
    board_id: str,
    board_update: schemas.BoardBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Update a board"""
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check project access
    check_project_access(board.project_id, current_user.id, db)
    
    # Update board
    board.name = board_update.name
    board.position = board_update.position
    
    db.commit()
    db.refresh(board)
    
    return board

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    board_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Delete a board"""
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check project access (and must be admin or owner)
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == board.project_id,
        models.ProjectMember.user_id == current_user.id
    ).first()
    
    if not membership or membership.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner or admin can delete boards"
        )
    
    db.delete(board)
    db.commit()
    
    return None