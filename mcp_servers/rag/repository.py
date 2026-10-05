import json
from pathlib import Path

from mcp_servers.rag.schemas import Exam


class ExamRepository:

    def __init__(
        self,
        data_path: Path,
    ) -> None:
        
        self.data_path = data_path

    def get_all(self) -> list[Exam]:

        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Exam database not found: "
                f"{self.data_path}"
            )

        raw_data = json.loads(
            self.data_path.read_text(
                encoding="utf-8"
            )
        )

        return [
            Exam.model_validate(item)
            for item in raw_data
        ]