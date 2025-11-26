from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CITIZEN = "citizen"
    OFFICER = "officer"
    ADMIN = "admin"

# Base shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    role: UserRole = UserRole.CITIZEN
    hashedDeviceId: Optional[str] = None  # Added for Anonymous Reporting

# Registration Input (For creating new registered users)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Required for Officers/Admins")

# Login Input
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Role Update Input (For Admin dashboard)
class UserUpdate(BaseModel):
    role: UserRole

# Output Response (Sanitized - No Passwords)
class UserResponse(UserBase):
    userId: str
    isAnonymous: bool
    createdAt: datetime
    
    class Config:
        from_attributes = True

# Profile Update Input
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None