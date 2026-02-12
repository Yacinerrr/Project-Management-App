from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional

#User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    avatar: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

#project schemas

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int 
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

#Board schemas

class BoardBase(BaseModel):
    name: str
    position: int 


class BoardCreate(BoardBase):
    project_id: str


class Board(BoardBase):
    id: int 
    created_at: datetime
    class Config:
        from_attributes = True


#column schemas

class ColumnBase(BaseModel):
    name: str
    position: int

class ColumnCreate(ColumnBase):
    board_id: str

class Column(ColumnBase):
    id :str
    created_at: datetime
    board_id: str
    class Config:
        from_attributes = True

#Task schemas

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date : Optional[datetime] = None

class TaskCreate(TaskBase):
    column_id: str
    position: int
    assignee_id: Optional[str] = None

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    column_id: Optional[str] = None
    position: Optional[int] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[str] = None

class Task(TaskBase):
    id:str
    Column_id: str
    position: int
    assignee_id: Optional[str] = None
    created_at: datetime
    created_by_id: str
    class Config:
        from_attributes = True


#comment schemas

class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    task_id: str

class Comment(CommentBase):
    id: str
    task_id: str
    user_id :str
    created_at: datetime
    class Config:
        from_attributes = True



