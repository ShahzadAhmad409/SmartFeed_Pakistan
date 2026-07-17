from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    organization_name: Optional[str] = None
    city: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    organization_name: Optional[str]
    city: Optional[str]
    
    class Config:
        from_attributes = True

class NGORequestCreate(BaseModel):
    organization_name: str
    registration_number: str
    contact_info: str
    city: str

class DonationCreate(BaseModel):
    food_name: str
    category: str
    quantity: int
    hours_before_expiry: int
    lat: float
    lng: float

class DonationOut(BaseModel):
    id: int
    food_name: str
    category: str
    quantity: int
    hours_before_expiry: int
    lat: float
    lng: float
    status: str
    created_at: datetime
    donor_id: int
    
    class Config:
        from_attributes = True
