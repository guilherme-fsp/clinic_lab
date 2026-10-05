from pydantic import BaseModel, Field


class ExamItem(BaseModel):
    name: str = Field(min_length=1)
    code: str = Field(min_length=1)


class AppointmentRequest(BaseModel):
    exams: list[ExamItem] = Field(
        min_length=1,
        description="Laboratory exams to be scheduled.",
    )


class AppointmentResponse(BaseModel):
    appointment_id: str
    status: str
    exams: list[ExamItem]
    message: str