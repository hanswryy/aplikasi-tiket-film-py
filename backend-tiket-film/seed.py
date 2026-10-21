from datetime import datetime, timedelta

from extensions import db
from models import Booking, BookingStatus, BookedSeat, Movie, Role, Showtime, Studio, User


def seed_database() -> None:
    """Reset and populate the database with the same records as the JS seed."""
    db.session.query(BookedSeat).delete()
    db.session.query(Booking).delete()
    db.session.query(Showtime).delete()
    db.session.query(Studio).delete()
    db.session.query(Movie).delete()
    db.session.query(User).delete()

    password = "password123"
    admin = User(email="admin@cinema.com", name="Admin XXI", role=Role.ADMIN)
    admin.set_password(password)
    customer = User(email="john@example.com", name="John Doe", role=Role.USER)
    customer.set_password(password)
    db.session.add_all([admin, customer])

    studio1 = Studio(name="Studio 1 XXI", capacity=100, total_rows=10, total_cols=10)
    studio2 = Studio(name="Studio 2 XXI", capacity=100, total_rows=10, total_cols=10)
    imax = Studio(name="IMAX 3D", capacity=120, total_rows=10, total_cols=12)
    db.session.add_all([studio1, studio2, imax])

    movie1 = Movie(
        title="Dune: Part Two",
        description="Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
        duration_min=166,
        poster_url="https://media.themoviedb.org/t/p/w220_and_h330_face/heM4XKC0jA8fTSNe8F7oUkcJV7Z.jpg",
    )
    movie2 = Movie(
        title="Spider-Man: Across the Spider-Verse",
        description="Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People charged with protecting its existence.",
        duration_min=140,
        poster_url="https://media.themoviedb.org/t/p/w220_and_h330_face/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
    )
    movie3 = Movie(
        title="Oppenheimer",
        description="The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
        duration_min=180,
        poster_url="https://media.themoviedb.org/t/p/w220_and_h330_face/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
    )
    db.session.add_all([movie1, movie2, movie3])
    db.session.flush()

    now = datetime.utcnow()
    start1 = now + timedelta(hours=3)
    start2 = now + timedelta(hours=24)
    start3 = now + timedelta(hours=2)
    showtime1 = Showtime(
        movie_id=movie1.id, studio_id=studio1.id, price=50000,
        start_time=start1, end_time=start1 + timedelta(minutes=movie1.duration_min),
    )
    showtime2 = Showtime(
        movie_id=movie2.id, studio_id=imax.id, price=75000,
        start_time=start2, end_time=start2 + timedelta(minutes=movie2.duration_min),
    )
    showtime3 = Showtime(
        movie_id=movie3.id, studio_id=studio2.id, price=50000,
        start_time=start3, end_time=start3 + timedelta(minutes=movie3.duration_min),
    )
    db.session.add_all([showtime1, showtime2, showtime3])
    db.session.flush()

    booking = Booking(
        user_id=customer.id,
        showtime_id=showtime1.id,
        total_amount=100000,
        status=BookingStatus.PAID,
    )
    db.session.add(booking)
    db.session.flush()
    db.session.add_all([
        BookedSeat(showtime_id=showtime1.id, booking_id=booking.id, row="A", number=1),
        BookedSeat(showtime_id=showtime1.id, booking_id=booking.id, row="A", number=2),
    ])
    db.session.commit()
