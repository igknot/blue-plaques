from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

plaque_categories = Table(
    'plaque_categories',
    Base.metadata,
    Column('plaque_id', Integer, ForeignKey('plaques.id', ondelete='CASCADE')),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'))
)

class Plaque(Base):
    __tablename__ = "plaques"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    inscription = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500))
    year_erected = Column(Integer)
    organization = Column(String(255))
    source_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = relationship("Image", back_populates="plaque", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=plaque_categories, back_populates="plaques")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    plaque_id = Column(Integer, ForeignKey('plaques.id', ondelete='CASCADE'), nullable=False)
    url = Column(String(500), nullable=False)
    caption = Column(String(500))
    photographer = Column(String(255))
    year_taken = Column(Integer)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    plaque = relationship("Plaque", back_populates="images")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    plaques = relationship("Plaque", secondary=plaque_categories, back_populates="categories")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
