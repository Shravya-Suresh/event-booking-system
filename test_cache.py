import requests
from cache import get_cached_seats, invalidate_seats_cache

# Step 1: populate cache
response = requests.get("http://localhost:8000/events/1/seats")
print("Seats before booking:", response.json())
print("Cache after GET:", get_cached_seats(1))

# Step 2: book seat 4 (currently available)
booking_response = requests.post("http://localhost:8000/bookings/", json={"user_id": 5, "seat_id": 4})
print("\nBooking response:", booking_response.json())

# Step 3: check cache immediately after booking — should be invalidated (None) or already refreshed
print("Cache immediately after booking:", get_cached_seats(1))

# Step 4: call the endpoint again — should reflect updated status
response2 = requests.get("http://localhost:8000/events/1/seats")
print("\nSeats after booking (via API):", response2.json())