from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from .. import models, schemas
from .. import auth as auth_utils
from ..database import get_db

router = APIRouter(prefix="/comments", tags=["Comments"])

def check_task_access(task_id: str, user_id: str, db: Session):
    """Helper function to check if user has access to a task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    column = db.query(models.BoardColumn).filter(models.BoardColumn.id == task.column_id).first()
    board = db.query(models.Board).filter(models.Board.id == column.board_id).first()
    
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == board.project_id,
        models.ProjectMember.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this task"
        )
    
    return task

@router.post("", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Create a new comment on a task"""
    # Check task access
    check_task_access(comment.task_id, current_user.id, db)
    
    # Create the comment
    new_comment = models.Comment(
        id=str(uuid.uuid4()),
        content=comment.content,
        task_id=comment.task_id,
        user_id=current_user.id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return new_comment

@router.get("/task/{task_id}", response_model=List[schemas.Comment])
def get_task_comments(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get all comments for a task"""
    # Check task access
    check_task_access(task_id, current_user.id, db)
    
    # Get all comments ordered by creation time
    comments = db.query(models.Comment).filter(
        models.Comment.task_id == task_id
    ).order_by(models.Comment.created_at).all()
    
    return comments

@router.put("/{comment_id}", response_model=schemas.Comment)
def update_comment(
    comment_id: str,
    content: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Update a comment (only by the author)"""
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user is the author
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments"
        )
    
    # Update comment
    comment.content = content
    
    db.commit()
    db.refresh(comment)
    
    return comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Delete a comment (only by the author)"""
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user is the author
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )
    
    db.delete(comment)
    db.commit()
    
    return None