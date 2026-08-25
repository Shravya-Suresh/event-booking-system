from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

import models
import schemas
from database import Base, engine, get_db
from cache import get_cached_seats, set_cached_seats, invalidate_seats_cache

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Users ---
@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Events ---
@app.post("/events/", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(name=event.name, total_seats=event.total_seats)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # auto-create seats for this event
    for seat_num in range(1, event.total_seats + 1):
        seat = models.Seat(event_id=db_event.id, seat_number=seat_num, status="available")
        db.add(seat)
    db.commit()

    return db_event


@app.post("/bookings/", response_model=schemas.BookingOut)
def book_seat(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    # Lock the seat row so no other transaction can read/modify it until we're done
    seat = db.query(models.Seat).filter(
        models.Seat.id == booking.seat_id
    ).with_for_update().first()

    if seat is None:
        raise HTTPException(status_code=404, detail="Seat not found")

    if seat.status == "booked":
        raise HTTPException(status_code=409, detail="Seat already booked")

    # Still holding the lock — safe to update
    seat.status = "booked"

    new_booking = models.Booking(user_id=booking.user_id, seat_id=booking.seat_id)
    db.add(new_booking)

    db.commit()
    db.refresh(new_booking)
    invalidate_seats_cache(seat.event_id)
    return new_booking

@app.post("/bookings/optimistic/", response_model=schemas.BookingOut)
def book_seat_optimistic(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    # Read without locking
    seat = db.query(models.Seat).filter(models.Seat.id == booking.seat_id).first()

    if seat is None:
        raise HTTPException(status_code=404, detail="Seat not found")

    if seat.status == "booked":
        raise HTTPException(status_code=409, detail="Seat already booked")

    current_version = seat.version

    # Attempt update ONLY if version hasn't changed since we read it
    result = db.query(models.Seat).filter(
        models.Seat.id == booking.seat_id,
        models.Seat.version == current_version
    ).update({
        "status": "booked",
        "version": current_version + 1
    })

    if result == 0:
        # Someone else updated it between our read and our write
        db.rollback()
        raise HTTPException(status_code=409, detail="Seat booking conflict, please retry")

    new_booking = models.Booking(user_id=booking.user_id, seat_id=booking.seat_id)
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    seat = db.query(models.Seat).filter(models.Seat.id == booking.seat_id).first()
    seat.status = "available"

    db.delete(booking)
    db.commit()
    invalidate_seats_cache(seat.event_id)

    return {"detail": "Booking cancelled, seat released"}

@app.get("/events/{event_id}/seats", response_model=list[schemas.SeatOut])
def get_seats(event_id: int, db: Session = Depends(get_db)):
    print("DEBUG: checking cache for event", event_id)
    cached = get_cached_seats(event_id)
    print("DEBUG: cache result was:", cached)
    if cached is not None:
        return cached

    seats = db.query(models.Seat).filter(models.Seat.event_id == event_id).all()
    seats_data = [schemas.SeatOut.model_validate(s).model_dump(mode="json") for s in seats]
    print("DEBUG: about to write to cache:", seats_data)
    set_cached_seats(event_id, seats_data)
    print("DEBUG: wrote to cache successfully")
    return seats_data