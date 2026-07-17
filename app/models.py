from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) # 'donor', 'receiver', 'admin', 'superadmin'
    organization_name = Column(String, nullable=True) # for donors/admins
    city = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    donations = relationship("Donation", back_populates="donor", foreign_keys="Donation.donor_id")
    claims = relationship("Donation", back_populates="receiver", foreign_keys="Donation.receiver_id")


class NGORequest(Base):
    __tablename__ = "ngo_requests"

    id = Column(Integer, primary_key=True, index=True)
    organization_name = Column(String, nullable=False)
    registration_number = Column(String, nullable=False)
    contact_info = Column(String, nullable=False)
    city = Column(String, nullable=False)
    status = Column(String, default="pending") # 'pending', 'approved', 'rejected'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False) # meals
    hours_before_expiry = Column(Integer, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True) # User who claimed it
    
    status = Column(String, default="available") # 'available', 'claimed'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    donor = relationship("User", back_populates="donations", foreign_keys=[donor_id])
    receiver = relationship("User", back_populates="claims", foreign_keys=[receiver_id])

