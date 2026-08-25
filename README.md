# Event Booking System

A backend API for booking event seats, built to handle concurrent booking requests safely — preventing double-booking when multiple users try to reserve the same seat at the same time.

## The Problem

When multiple users attempt to book the same seat simultaneously, a naive "check then update" approach creates a race condition: two requests can both read a seat as "available" before either one writes "booked," resulting in the same seat being double-booked.

## The Solution

This project implements and compares **two concurrency control strategies**:

1. **Pessimistic locking** (`SELECT ... FOR UPDATE`) — locks the seat row during the transaction, forcing concurrent requests to wait until the first transaction completes.
2. **Optimistic locking** (version-based) — allows concurrent reads, but rejects writes if the seat's version number changed since it was read, avoiding held locks at the cost of requiring retries under contention.

Both were validated with automated concurrency tests firing 10 simultaneous requests at the same seat — resulting in exactly 1 success and 9 correctly rejected requests every time.

Additionally, the system uses **Redis caching** for seat availability reads (a read-heavy operation), with **cache invalidation on every booking/cancellation** to guarantee users never see stale seat data.

## Tech Stack
- **FastAPI** — REST API framework
- **PostgreSQL** — relational database
- **SQLAlchemy** — ORM
- **Redis** — caching layer

## Features
- Create events with auto-generated seats
- Book a seat (pessimistic or optimistic locking endpoint)
- Cancel a booking (releases the seat)
- View seat availability (cached, with automatic invalidation on writes)

## Concurrency Test Results
