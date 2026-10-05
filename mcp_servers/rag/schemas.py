from pydantic import BaseModel, Field


class Exam(BaseModel):
    name: str
    code: str


class ExamMatch(BaseModel):
    name: str
    code: str

    score: float = Field(
        ge=0,
    )


class ExamSearchResult(BaseModel):
    query: str
    matches: list[ExamMatch]