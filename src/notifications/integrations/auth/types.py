import datetime
import uuid

from pydantic import BaseModel, EmailStr


class BoundaryRegistrationDate(BaseModel):
    """Даты регистрации первого и последнего пользователей."""

    first_registration_date: datetime.date
    last_registration_date: datetime.date


class UserDetail(BaseModel):
    """Информация о пользователе."""

    pk: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    registration_date: datetime.date
