from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Association table for task labels
task_labels = Table(
    'task_labels',
    Base.metadata,
    Column('task_id', String, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('label_id', String, ForeignKey('labels.id', ondelete='CASCADE'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    avatar = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    projects = relationship("ProjectMember", back_populates="user")
    tasks_created = relationship("Task", back_populates="created_by", foreign_keys="Task.created_by_id")
    tasks_assigned = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    comments = relationship("Comment", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    members = relationship("ProjectMember", back_populates="project")
    boards = relationship("Board", back_populates="project")

class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(String, primary_key=True, index=True)
    role = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="projects")
    project = relationship("Project", back_populates="members")

class Board(Base):
    __tablename__ = "boards"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="boards")
    columns = relationship("Column", back_populates="board")

class Column(Base):
    __tablename__ = "columns"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    board_id = Column(String, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    column_id = Column(String, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    priority = Column(String)
    due_date = Column(DateTime(timezone=True))
    created_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    column = relationship("Column", back_populates="tasks")
    created_by = relationship("User", back_populates="tasks_created", foreign_keys=[created_by_id])
    assignee = relationship("User", back_populates="tasks_assigned", foreign_keys=[assignee_id])
    comments = relationship("Comment", back_populates="task")
    labels = relationship("Label", secondary=task_labels, back_populates="tasks")

class Label(Base):
    __tablename__ = "labels"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tasks = relationship("Task", secondary=task_labels, back_populates="labels")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True, index=True)
    content = Column(String, nullable=False)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")