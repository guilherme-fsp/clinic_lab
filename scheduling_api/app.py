from fastapi import FastAPI, status

from scheduling_api.schemas import (
    AppointmentRequest,
    AppointmentResponse,
)
from scheduling_api.service import (
    create_appointment,
)


app = FastAPI(
    title="Laboratory Scheduling API",
    description=(
        "Fictitious API responsible for receiving "
        "laboratory exam scheduling requests."
    ),
    version="1.0.0",
)


@app.get(
    "/health",
    tags=["Health"],
)
def health_check() -> dict[str, str]:
    return {
        "status": "ok"
    }


@app.post(
    "/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Appointments"],
    summary="Create an appointment request",
)
def schedule_appointment(
    request: AppointmentRequest,
) -> AppointmentResponse:

    return create_appointment(request)