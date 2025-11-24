# backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(Text, nullable=False)
    doc_type = Column(String(10), nullable=False)  # "docx" or "pptx"
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="projects")
    sections = relationship("Section", back_populates="project", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="sections")
    refinements = relationship("RefinementHistory", back_populates="section", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="section", cascade="all, delete-orphan")

class RefinementHistory(Base):
    __tablename__ = "refinement_history"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    old_content = Column(Text, nullable=True)
    new_content = Column(Text, nullable=True)
    prompt = Column(Text, nullable=True)
    liked = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("Section", back_populates="refinements")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("Section", back_populates="comments")
