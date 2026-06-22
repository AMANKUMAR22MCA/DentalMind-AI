from datetime import datetime

from langchain_core.messages import AIMessage

from app.agent.state import AgentState
from datetime import date, datetime
from app.agent.tools.appointments import (
    get_available_slots,
    book_appointment,
)


async def book_node(
    state: AgentState,
) -> AgentState:
    """
    Multi-turn appointment booking flow.
    """


    user_message = (
        state["messages"][-1].content
    )


    # --------------------------------
    # STEP 1:
    # Need appointment date
    # --------------------------------

    if "appointment_date" not in state:


        try:

            appointment_date = (
                datetime
                .strptime(
                    user_message,
                    "%Y-%m-%d",
                )
                .date()
            )


            state["appointment_date"] = (
                appointment_date
            )


        except ValueError:


            state["messages"].append(

                AIMessage(
                    content=(
                        "Sure, I can help you book an appointment. "
                        "Please provide appointment date "
                        "in YYYY-MM-DD format."
                    )
                )

            )


            return state



    # --------------------------------
    # STEP 2:
    # Fetch available slots
    # --------------------------------

    if "available_slots" not in state:


        slots = await get_available_slots(

            state["appointment_date"]

        )


        state["available_slots"] = slots


        if not slots:


            state["messages"].append(

                AIMessage(
                    content=(
                        "No slots available for this date. "
                        "Please choose another date."
                    )
                )

            )


            return state



        state["messages"].append(

            AIMessage(
                content=(
                    "Available slots are:\n"
                    + "\n".join(slots)
                    + "\n\nPlease choose a slot."
                )
            )

        )


        return state



    # --------------------------------
    # STEP 3:
    # User selects slot
    # --------------------------------

    if "selected_slot" not in state:


        if (
            user_message
            not in state["available_slots"]
        ):


            state["messages"].append(

                AIMessage(
                    content=(
                        "Please select a valid slot "
                        "from available slots."
                    )
                )

            )


            return state



        state["selected_slot"] = (
            user_message
        )


        state["messages"].append(

            AIMessage(
                content=(
                    "Great. Please provide your "
                    "name and email separated by comma.\n\n"
                    "Example:\n"
                    "Aman Kumar, aman@gmail.com"
                )
            )

        )


        return state



    # --------------------------------
    # STEP 4:
    # collect name + email
    # create booking
    # --------------------------------

    if (
        "patient_name" not in state
        or "user_email" not in state
    ):


        try:


            name, email = (

                user_message
                .split(",")

            )


            state["patient_name"] = (
                name.strip()
            )


            state["user_email"] = (
                email.strip()
            )



        except ValueError:


            state["messages"].append(

                AIMessage(
                    content=(
                        "Please send name and email "
                        "in correct format:\n"
                        "Name, email@example.com"
                    )
                )

            )


            return state



    # --------------------------------
    # STEP 5:
    # Book appointment
    # --------------------------------

    try:

        # convert string back to date if needed
        appt_date = state["appointment_date"]
        if isinstance(appt_date, str):
            appt_date = datetime.strptime(
                appt_date, "%Y-%m-%d"
            ).date()
        appointment = await book_appointment(
            patient_name=state["patient_name"],
            patient_email=state["user_email"],
            appointment_date=appt_date,  # ← fixed!
            slot_time=state["selected_slot"],
        )    
 

        state["messages"].append(

            AIMessage(

                content=(
                    "Appointment booked successfully.\n\n"
                    f"Booking ID: {appointment.id}\n"
                    f"Date: {appointment.appointment_date}\n"
                    f"Time: {appointment.slot_time}"
                )

            )

        )


    except Exception as error:


        state["messages"].append(

            AIMessage(
                content=str(error)
            )

        )


    return state