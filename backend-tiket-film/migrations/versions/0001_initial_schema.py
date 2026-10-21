"""Create the cinema schema matching Prisma.

Revision ID: 0001_initial_schema
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    role = sa.Enum("USER", "ADMIN", name="Role", create_type=False)
    booking_status = sa.Enum(
        "PENDING",
        "PAID",
        "CANCELLED",
        "EXPIRED",
        name="BookingStatus",
        create_type=False,
    )
    bind = op.get_bind()
    role.create(bind, checkfirst=True)
    booking_status.create(bind, checkfirst=True)

    op.create_table(
        "User",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", role, nullable=False, server_default="USER"),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name="User_pkey"),
        sa.UniqueConstraint("email", name="User_email_key"),
    )
    op.create_table(
        "Movie",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("posterUrl", sa.String(), nullable=False),
        sa.Column("durationMin", sa.Integer(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name="Movie_pkey"),
    )
    op.create_table(
        "Studio",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("totalRows", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("totalCols", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name="Studio_pkey"),
    )
    op.create_table(
        "Showtime",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("movieId", sa.String(), nullable=False),
        sa.Column("studioId", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("startTime", sa.DateTime(), nullable=False),
        sa.Column("endTime", sa.DateTime(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updatedAt", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["movieId"], ["Movie.id"], name="Showtime_movieId_fkey", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["studioId"], ["Studio.id"], name="Showtime_studioId_fkey", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="Showtime_pkey"),
    )
    op.create_table(
        "Booking",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("userId", sa.String(), nullable=False),
        sa.Column("showtimeId", sa.String(), nullable=False),
        sa.Column("totalAmount", sa.Float(), nullable=False),
        sa.Column("status", booking_status, nullable=False, server_default="PENDING"),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updatedAt", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["showtimeId"], ["Showtime.id"], name="Booking_showtimeId_fkey", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["userId"], ["User.id"], name="Booking_userId_fkey", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="Booking_pkey"),
    )
    op.create_table(
        "BookedSeat",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("showtimeId", sa.String(), nullable=False),
        sa.Column("bookingId", sa.String(), nullable=False),
        sa.Column("row", sa.String(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["bookingId"], ["Booking.id"], name="BookedSeat_bookingId_fkey", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["showtimeId"], ["Showtime.id"], name="BookedSeat_showtimeId_fkey", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="BookedSeat_pkey"),
        sa.UniqueConstraint("showtimeId", "row", "number", name="BookedSeat_showtimeId_row_number_key"),
    )


def downgrade() -> None:
    op.drop_table("BookedSeat")
    op.drop_table("Booking")
    op.drop_table("Showtime")
    op.drop_table("Studio")
    op.drop_table("Movie")
    op.drop_table("User")
    bind = op.get_bind()
    sa.Enum(name="BookingStatus").drop(bind, checkfirst=True)
    sa.Enum(name="Role").drop(bind, checkfirst=True)
