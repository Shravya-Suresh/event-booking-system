import requests
import threading
import time

URL = "http://localhost:8000/bookings/"
SEAT_ID = 3  # use a fresh, still-available seat
NUM_REQUESTS = 10

results = []

def try_book(user_id):
    start = time.time()
    response = requests.post(URL, json={"user_id": user_id, "seat_id": SEAT_ID})
    elapsed = time.time() - start
    results.append((user_id, response.status_code, response.json(), elapsed))

threads = []
for i in range(5, 5 + NUM_REQUESTS):
    t = threading.Thread(target=try_book, args=(i,))
    threads.append(t)

overall_start = time.time()

for t in threads:
    t.start()
for t in threads:
    t.join()

overall_elapsed = time.time() - overall_start

success_count = 0
for user_id, status, body, elapsed in results:
    print(f"User {user_id}: status={status}, time={elapsed:.3f}s, body={body}")
    if status == 200:
        success_count += 1

avg_time = sum(r[3] for r in results) / len(results)
print(f"\nTotal successful bookings: {success_count} (should be exactly 1)")
print(f"Total wall-clock time for all {NUM_REQUESTS} requests: {overall_elapsed:.3f}s")
print(f"Average individual request time: {avg_time:.3f}s")