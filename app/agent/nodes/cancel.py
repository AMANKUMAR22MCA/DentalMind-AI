import uuid

from langchain_core.messages import AIMessage

from app.agent.state import AgentState

from app.agent.tools.appointments import (
    cancel_appointment,
)


async def cancel_node(
    state: AgentState,
) -> AgentState:
    """
    Handles appointment cancellation flow.
    """

    user_message = (
        state["messages"][-1].content
    )


    # -----------------------------
    # STEP 0:
    # Handle reschedule response
    # -----------------------------

    if state.get("appointment_cancelled"):


        if any(
            word in user_message.lower()
            for word in [
                "yes",
                "yeah",
                "sure",
                "reschedule",
            ]
        ):


            # clear old booking/cancel state

            state.pop("appointment_date", None)
            state.pop("available_slots", None)
            state.pop("selected_slot", None)
            state.pop("patient_name", None)
            state.pop("user_email", None)

            state.pop(
                "cancel_booking_id",
                None,
            )

            state.pop(
                "appointment_cancelled",
                None,
            )


            state["intent"] = "book"


            state["messages"].append(

                AIMessage(
                    content=(
                        "Sure! Let's reschedule. "
                        "Please provide your preferred date "
                        "in YYYY-MM-DD format."
                    )
                )

            )


        else:


            state["messages"].append(

                AIMessage(
                    content=(
                        "Okay! Feel free to reach out "
                        "anytime. Have a great day!"
                    )
                )

            )


        return state



    # -----------------------------
    # STEP 1:
    # Collect booking ID
    # -----------------------------

    if "cancel_booking_id" not in state:


        if "cancel" in user_message.lower():


            state["messages"].append(

                AIMessage(
                    content=(
                        "Sure, I can help cancel "
                        "your appointment. "
                        "Please provide your booking ID."
                    )
                )

            )

            return state



        # validate UUID

        try:


            uuid.UUID(
                user_message.strip()
            )


            state["cancel_booking_id"] = (
                user_message.strip()
            )


        except ValueError:


            state["messages"].append(

                AIMessage(
                    content=(
                        "Please provide a valid booking ID."
                    )
                )

            )

            return state



    # -----------------------------
    # STEP 2:
    # Cancel appointment
    # -----------------------------

    success = await cancel_appointment(

        state["cancel_booking_id"]

    )


    if success:


        state["appointment_cancelled"] = True


        state["messages"].append(

            AIMessage(
                content=(
                    "Your appointment has been "
                    "cancelled successfully.\n\n"
                    "Would you like to reschedule?"
                )
            )

        )


    else:


        state["messages"].append(

            AIMessage(
                content=(
                    "I could not find an appointment "
                    "with that booking ID."
                )
            )

        )


    return state