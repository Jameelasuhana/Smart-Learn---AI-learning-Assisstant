from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    email: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
