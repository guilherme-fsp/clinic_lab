from uuid import uuid4

from scheduling_api.schemas import (
    AppointmentRequest,
    AppointmentResponse,
)


def create_appointment(
    request: AppointmentRequest,
) -> AppointmentResponse:

    appointment_id = (
        f"APT-{uuid4().hex[:8]}"
    )

    return AppointmentResponse(
        appointment_id=appointment_id,
        status="requested",
        exams=request.exams,
        message=(
            "Appointment request received successfully."
        ),
    )