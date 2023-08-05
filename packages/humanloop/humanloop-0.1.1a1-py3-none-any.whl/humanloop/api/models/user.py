from pydantic import BaseModel


class UserResponse(BaseModel):
    """Response model for /me endpoint"""

    email_address: str
