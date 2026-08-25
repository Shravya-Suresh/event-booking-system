from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    name: str
    total_seats: int

class EventOut(BaseModel):
    id: int
    name: str
    total_seats: int
    class Config:
        from_attributes = True

class SeatOut(BaseModel):
    id: int
    seat_number: int
    status: str
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    user_id: int
    seat_id: int

class BookingOut(BaseModel):
    id: int
    user_id: int
    seat_id: int
    booked_at: datetime
    class Config:
        from_attributes = True