from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from .. import models, schemas
from .. import auth as auth_utils
from ..database import get_db

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Create a new project"""
    # Create the project
    new_project = models.Project(
        id=str(uuid.uuid4()),
        name=project.name,
        description=project.description
    )
    
    db.add(new_project)
    db.flush()  # Get the project ID before committing
    
    # Add current user as project owner
    project_member = models.ProjectMember(
        id=str(uuid.uuid4()),
        role="owner",
        user_id=current_user.id,
        project_id=new_project.id
    )
    
    db.add(project_member)
    db.commit()
    db.refresh(new_project)
    
    return new_project

@router.get("", response_model=List[schemas.Project])
def get_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get all projects for the current user"""
    # Get all projects where user is a member
    projects = db.query(models.Project).join(
        models.ProjectMember
    ).filter(
        models.ProjectMember.user_id == current_user.id
    ).all()
    
    return projects

@router.get("/{project_id}", response_model=schemas.Project)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get a specific project by ID"""
    # Check if user is a member of this project
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access"
        )
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: str,
    project_update: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Update a project"""
    # Check if user is owner or admin
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == current_user.id
    ).first()
    
    if not membership or membership.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this project"
        )
    
    # Get and update the project
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.name = project_update.name
    project.description = project_update.description
    
    db.commit()
    db.refresh(project)
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Delete a project (owner only)"""
    # Check if user is owner
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == current_user.id
    ).first()
    
    if not membership or membership.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete the project"
        )
    
    # Delete the project (cascades to members, boards, etc.)
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()
    
    return None

@router.get("/{project_id}/members", response_model=List[schemas.User])
def get_project_members(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Get all members of a project"""
    # Check if user is a member
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access"
        )
    
    # Get all members
    members = db.query(models.User).join(
        models.ProjectMember
    ).filter(
        models.ProjectMember.project_id == project_id
    ).all()
    
    return members

@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: str,
    member_email: str,
    role: str = "member",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """Add a member to a project (admin or owner only)"""
    # Check if user is owner or admin
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == current_user.id
    ).first()
    
    if not membership or membership.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add members"
        )
    
    # Find the user to add
    user_to_add = db.query(models.User).filter(models.User.email == member_email).first()
    
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already a member
    existing_member = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == user_to_add.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project"
        )
    
    # Add the member
    new_member = models.ProjectMember(
        id=str(uuid.uuid4()),
        role=role,
        user_id=user_to_add.id,
        project_id=project_id
    )
    
    db.add(new_member)
    db.commit()
    
    return {"message": "Member added successfully"}