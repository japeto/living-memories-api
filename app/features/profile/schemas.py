from pydantic import BaseModel, EmailStr


class UserProfileResponse(BaseModel):
    user_id: str
    email: EmailStr
    display_name: str
    full_name: str | None = None
    avatar_url: str | None = None
