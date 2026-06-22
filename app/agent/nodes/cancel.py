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
    # STEP 1:
    # Collect booking ID
    # -----------------------------

    if "cancel_booking_id" not in state:


        # User just started cancellation

        if "cancel" in user_message.lower():


            state["messages"].append(

                AIMessage(
                    content=(
                        "Sure, I can help cancel your appointment. "
                        "Please provide your booking ID."
                    )
                )

            )


            return state



        # Validate booking ID format

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


        state["messages"].append(

            AIMessage(
                content=(
                    "Your appointment has been "
                    "cancelled successfully.\n\n"
                    "Would you like to reschedule?"
                )
            )

        )


        state["appointment_cancelled"] = True



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