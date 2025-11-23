from app.core.database import BaseOps  # ✅ Import correct base

# Import all models
from app.models.user import User
from app.models.report import Report
from app.models.attachment import Attachment

# Export for convenience
__all__ = ['BaseOps', 'User', 'Report', 'Attachment']