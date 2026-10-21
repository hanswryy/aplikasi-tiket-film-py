# Backend Tiket Film (Flask)

Flask counterpart of `backend-tiket-film-js`. The package layout mirrors the
NestJS domains: `auth`, `movies`, `studios`, `showtimes`, and `bookings`.

## Setup

```powershell
cd backend-tiket-film
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

The API runs on `http://localhost:3000`. The default local database is SQLite
(`cinema.db`). Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL when using the
shared PostgreSQL container, for example:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgrespassword@localhost:5433/cinema_db
```

Implemented endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `GET /movies`
- `GET /movies/<id>`
- `GET /studios`
- `GET /studios/<id>`
- `GET /showtimes`
- `GET /showtimes/<id>`
- `POST /bookings`
- `GET /bookings/my-bookings`
- `POST /bookings/<id>/pay`
- `POST /bookings/midtrans/notification`

Movie mutation endpoints and user listing/detail/deletion are intentionally not
exposed yet.

## Midtrans configuration

Payment endpoints use the `midtransclient` Snap SDK. Configure the following
variables in `.env`:

```env
MIDTRANS_SERVER_KEY=your-server-key
MIDTRANS_CLIENT_KEY=your-client-key
MIDTRANS_IS_PRODUCTION=false
```

`POST /bookings/<id>/pay` requires the booking owner and a `PENDING` booking.
It returns the Midtrans payment token and redirect URL. Midtrans notification
requests are verified through the SDK before the booking status is updated.
The notification handler is idempotent for bookings already marked `PAID`.

Booking creation and booking history require a JWT for a user with the `USER`
role. Booking creation validates the showtime, studio seat boundaries, seat
rows, duplicate seats, and database uniqueness conflicts. It creates the
booking and booked seats in one transaction with `PENDING` status.

`GET /bookings/my-bookings` returns the authenticated user's bookings ordered
newest first, including status, total amount, showtime, movie, studio, and
booked seats.

Studio and showtime administration is available to JWT-authenticated users
with the `ADMIN` role:

- `POST`, `PATCH`, and `DELETE /studios`
- `POST`, `PATCH`, and `DELETE /showtimes`

Showtime detail responses include the movie, studio, booked seats, total seat
capacity, booked-seat count, and available-seat count. New or updated
showtimes are rejected when their movie or studio does not exist, or when
their time range overlaps another showtime in the same studio.

## Request DTO validation

Marshmallow schemas are grouped with their domain modules:

- `auth/schemas.py`: registration and login payloads
- `movies/schemas.py`: movie create/update payloads and search query
- `studios/schemas.py`: studio create/update payloads
- `showtimes/schemas.py`: showtime create/update payloads and time-range validation
- `bookings/schemas.py`: booking payloads, nested seats, and duplicate-seat validation

The schemas for endpoints that are not exposed yet are ready for the
corresponding service routes. Registration, login, and movie search currently
use the schemas directly.
