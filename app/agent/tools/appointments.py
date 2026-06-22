import uuid

from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import AsyncSessionLocal
from app.models import Appointment


# -----------------------------
# Clinic working slots
# -----------------------------

ALL_SLOTS = [
    "9:00 AM",
    "10:00 AM",
    "11:00 AM",
    "12:00 PM",
    "1:00 PM",
    "2:00 PM",
    "3:00 PM",
    "4:00 PM",
    "5:00 PM",
    "6:00 PM",
]


# -----------------------------
# Get Available Slots
# -----------------------------

async def get_available_slots(
    appointment_date: date,
) -> list[str]:
    """
    Return free appointment slots
    for a given date.
    """


    # block past dates

    if appointment_date < date.today():

        return []


    # block Sunday
    # weekday():
    # Monday=0 ... Sunday=6

    if appointment_date.weekday() == 6:

        return []


    async with AsyncSessionLocal() as session:


        result = await session.execute(

            select(Appointment)
            .where(

                Appointment.appointment_date
                == appointment_date,


                Appointment.status
                == "booked",

            )

        )


        booked_appointments = (
            result.scalars().all()
        )


        booked_slots = {

            appointment.slot_time

            for appointment
            in booked_appointments

        }


        available_slots = [

            slot

            for slot in ALL_SLOTS

            if slot not in booked_slots

        ]


        return available_slots



# -----------------------------
# Book Appointment
# -----------------------------

async def book_appointment(
    patient_name: str,
    patient_email: str,
    appointment_date: date,
    slot_time: str,
) -> Appointment:
    """
    Create a new appointment.
    """


    # block past dates

    if appointment_date < date.today():

        raise ValueError(
            "Cannot book appointment in the past"
        )


    # block Sunday

    if appointment_date.weekday() == 6:

        raise ValueError(
            "Clinic is closed on Sunday"
        )


    # validate clinic slot

    if slot_time not in ALL_SLOTS:

        raise ValueError(
            "Invalid appointment slot"
        )


    async with AsyncSessionLocal() as session:


        appointment = Appointment(

            patient_name=patient_name,

            patient_email=patient_email,

            appointment_date=appointment_date,

            slot_time=slot_time,

        )


        try:


            session.add(
                appointment
            )


            await session.commit()


            await session.refresh(
                appointment
            )


            return appointment


        except IntegrityError:


            await session.rollback()


            raise ValueError(
                "This slot is already booked"
            )



# -----------------------------
# Cancel Appointment
# -----------------------------

async def cancel_appointment(
    appointment_id: str,
) -> bool:
    """
    Cancel existing appointment.
    """


    async with AsyncSessionLocal() as session:


        result = await session.execute(

            select(Appointment)
            .where(

                Appointment.id
                == uuid.UUID(
                    appointment_id
                )

            )

        )


        appointment = (
            result.scalars().first()
        )


        if not appointment:

            return False


        if appointment.status == "cancelled":

            return False


        appointment.status = "cancelled"


        await session.commit()


        return True