from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from .. import models, schemas
from .. import auth as auth_utils
from ..database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def check_column_access(column_id: str, user_id: str, db: Session):
    """Helper function to check if user has access to a column"""
    column = db.query(models.BoardColumn).filter(models.BoardColumn.id == column_id).first()
    
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    board = db.query(models.Board).filter(models.Board.id == column.board_id).first()
    
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == board.project_id,
        models.ProjectMember.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this column"
        )
    
    return column

@router.post("", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Create a new task"""
    # Check column access
    column = check_column_access(task.column_id, current_user.id, db)
    
    # Validate assignee if provided
    if task.assignee_id:
        assignee = db.query(models.User).filter(models.User.id == task.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{task.assignee_id}' not found"
            )
        
        # Optional: Check if assignee is a member of the project
        board = db.query(models.Board).filter(models.Board.id == column.board_id).first()
        assignee_membership = db.query(models.ProjectMember).filter(
            models.ProjectMember.project_id == board.project_id,
            models.ProjectMember.user_id == task.assignee_id
        ).first()
        
        if not assignee_membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User '{assignee.name or assignee.email}' is not a member of this project"
            )
    
    # Create the task
    new_task = models.Task(
        id=str(uuid.uuid4()),
        title=task.title,
        description=task.description,
        column_id=task.column_id,
        position=task.position,
        priority=task.priority,
        due_date=task.due_date,
        created_by_id=current_user.id,
        assignee_id=task.assignee_id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task

@router.get("/column/{column_id}", response_model=List[schemas.Task])
def get_column_tasks(
    column_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get all tasks in a column"""
    # Check column access
    check_column_access(column_id, current_user.id, db)
    
    # Get all tasks ordered by position
    tasks = db.query(models.Task).filter(
        models.Task.column_id == column_id
    ).order_by(models.Task.position).all()
    
    return tasks

@router.get("/{task_id}", response_model=schemas.Task)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get a specific task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check column access
    check_column_access(task.column_id, current_user.id, db)
    
    return task

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: str,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Update a task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check column access
    column = check_column_access(task.column_id, current_user.id, db)
    
    # Update task fields if provided
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.column_id is not None:
        # Check access to new column too
        check_column_access(task_update.column_id, current_user.id, db)
        task.column_id = task_update.column_id
    if task_update.position is not None:
        task.position = task_update.position
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.assignee_id is not None:
        # Validate assignee exists
        assignee = db.query(models.User).filter(models.User.id == task_update.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{task_update.assignee_id}' not found"
            )
        
        # Optional: Check if assignee is a member of the project
        board = db.query(models.Board).filter(models.Board.id == column.board_id).first()
        assignee_membership = db.query(models.ProjectMember).filter(
            models.ProjectMember.project_id == board.project_id,
            models.ProjectMember.user_id == task_update.assignee_id
        ).first()
        
        if not assignee_membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User '{assignee.name or assignee.email}' is not a member of this project"
            )
        
        task.assignee_id = task_update.assignee_id
    
    db.commit()
    db.refresh(task)
    
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Delete a task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check column access
    check_column_access(task.column_id, current_user.id, db)
    
    db.delete(task)
    db.commit()
    
    return None

@router.post("/{task_id}/move", response_model=schemas.Task)
def move_task(
    task_id: str,
    new_column_id: str,
    new_position: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Move a task to a different column or position (for drag-and-drop)"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check access to both columns
    check_column_access(task.column_id, current_user.id, db)
    check_column_access(new_column_id, current_user.id, db)
    
    # Update task position and column
    task.column_id = new_column_id
    task.position = new_position
    
    db.commit()
    db.refresh(task)
    
    return task