# Aplikasi Tiket Film

A cinema ticket booking application with a Vue frontend, Flask backend,
PostgreSQL database, SQLAlchemy ORM, and Docker Compose.

## Requirements

- Docker Desktop with Docker Compose
- Python 3.12 or later for local backend development
- Node.js 22 or later for frontend development
- npm

## Run With Docker

Run these commands from the project root:

```powershell
docker compose up -d --build
```

The services are exposed at:

- Frontend: http://localhost:8081
- Backend API: http://localhost:3001
- PostgreSQL: localhost:5434

Check service status:

```powershell
docker compose ps
```

View logs:

```powershell
docker compose logs -f
```

View only backend logs:

```powershell
docker compose logs -f backend
```

Stop the services while keeping the database volume:

```powershell
docker compose down
```

Remove the services and database data:

```powershell
docker compose down -v
```

The last command is destructive and removes the PostgreSQL volume.


## Local Development Without Docker

### Backend

Start PostgreSQL separately, then configure `backend-tiket-film/.env` with a local connection string:

```env
DATABASE_URL="postgresql+psycopg://postgres:postgrespassword@localhost:5433/cinema_db"
JWT_SECRET="replace-with-a-random-secret-at-least-32-characters"
PORT=3000
MIDTRANS_SERVER_KEY="your-server-key"
MIDTRANS_CLIENT_KEY="your-client-key"
MIDTRANS_IS_PRODUCTION=false
```

Install dependencies and start the Flask backend:

```powershell
cd backend-tiket-film
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

The Docker backend runs at http://localhost:3001.

### Frontend
In a second terminal:

```powershell
cd frontend-tiket-film
npm install
npm run dev
```

The Vite development server runs at the URL shown in the terminal. API requests use the local Vite proxy and are forwarded to the backend container.

## Database Commands

For a new Flask-managed database, apply the initial schema and sample data:

```powershell
cd backend-tiket-film
flask --app app db upgrade
flask --app app seed
```

The seed command intentionally clears existing cinema records before inserting
the same users, studios, movies, showtimes, booking, and seats as the JS seed.
Do not run it against a database that contains data you need to preserve.

The Flask migration is for first-time initialization. An existing database
already created by Prisma should not be upgraded with this initial migration.
