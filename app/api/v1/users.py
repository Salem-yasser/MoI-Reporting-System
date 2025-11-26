from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db_ops
from app.api.v1.auth import get_current_user
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserUpdate, UserRole

router = APIRouter()

@router.put("/{user_id}/role", response_model=UserResponse)
def assign_role(
    user_id: str,
    role_data: UserUpdate,
    db: Session = Depends(get_db_ops),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Assign a role to a user (e.g., promote Citizen to Officer).
    **Requirement:** Requester must be an ADMIN.
    """
    # 1. Enforce RBAC (Role Based Access Control)
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin privileges required."
        )
    
    # 2. Prevent an Admin from demoting themselves (Safety check)
    if user_id == current_user.userId and role_data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot demote yourself."
        )

    # 3. Update Role
    return UserService.update_role(db, user_id, role_data)