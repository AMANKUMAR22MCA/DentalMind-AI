import uuid

from datetime import date, datetime

from sqlalchemy import (
    String,
    Date,
    DateTime,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from sqlalchemy.sql import func

from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Appointment(Base):

    __tablename__ = "appointments"


    __table_args__ = (

        UniqueConstraint(
            "appointment_date",
            "slot_time",
            name="uq_appointment_slot",
        ),

    )


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


    patient_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    patient_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    appointment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )


    slot_time: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )


    status: Mapped[str] = mapped_column(
        String(20),
        default="booked",
        nullable=False,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )