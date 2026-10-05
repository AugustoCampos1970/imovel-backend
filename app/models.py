"""Modelos SQLAlchemy (tabelas)."""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    property_type = Column(String(50), nullable=False, index=True)
    purpose = Column(String(50), nullable=False, default="comprar", index=True)
    price = Column(Float, nullable=False, index=True)
    bedrooms = Column(Integer, nullable=False, default=0, index=True)
    bathrooms = Column(Integer, nullable=False, default=0)
    area_sqm = Column(Float, nullable=False, default=0)
    location = Column(String(255), nullable=False)
    neighborhood = Column(String(150), nullable=False, default="", index=True)
    city = Column(String(150), nullable=False, index=True)
    state = Column(String(2), nullable=False)
    image_url = Column(Text, nullable=False, default="")
    featured = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(
        Integer,
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(String(64), nullable=False, default="guest", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
