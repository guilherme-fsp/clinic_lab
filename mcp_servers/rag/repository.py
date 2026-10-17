import json
from pathlib import Path

from mcp_servers.rag.schemas import Exam
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

class ExamRepository:

    def __init__(
        self,
        data_path: Path,
    ) -> None:
        
        self.data_path = data_path
        logger.info("ExamRepository initialized with data path: %s", self.data_path)

    def get_all(self) -> list[Exam]:
        logger.info("ExamRepository: Retrieving all exams from data path: %s", self.data_path)

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