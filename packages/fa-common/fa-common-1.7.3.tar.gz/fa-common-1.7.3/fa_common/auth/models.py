from datetime import datetime
from typing import List, Optional

from pydantic import AnyUrl, EmailStr, Field, root_validator

from fa_common.models import CamelModel


class AuthUser(CamelModel):
    sub: str
    name: str = "Unknown User"
    given_name: Optional[str]
    family_name: Optional[str]
    country: Optional[str]
    email: Optional[EmailStr]
    nickname: Optional[str] = None
    emails: Optional[List[EmailStr]]
    email_verified: bool = Field(False, title="Email Verified")
    picture: Optional[AnyUrl] = None
    updated_at: Optional[datetime] = Field(None, title="Updated At")
    scopes: List[str] = []
    roles: List[str] = []

    @root_validator
    def set_name_to_given_family(cls, values):
        # sourcery skip: use-fstring-for-concatenation
        given = values.get("given_name", "")
        family = values.get("family_name", "")
        name = values.get("name")
        if (name is None or name == "Unknown User") and (given or family):
            new_name = f"{given} {family}"
            values["name"] = new_name

        return values
