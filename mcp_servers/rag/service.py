import re
import unicodedata

from rank_bm25 import BM25Okapi

from mcp_servers.rag.repository import (
    ExamRepository,
)
from mcp_servers.rag.schemas import (
    ExamMatch,
    ExamSearchResult,
)

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

logger.info("ExamRAGService: Initializing service")
def normalize_text(
    text: str,
) -> str:
    logger.info("normalize_text: Normalizing text: %s", text)

    normalized = unicodedata.normalize(
        "NFKD",
        text,
    )

    normalized = "".join(
        char
        for char in normalized
        if not unicodedata.combining(char)
    )

    normalized = normalized.lower()

    normalized = re.sub(
        r"[^a-z0-9\s]",
        " ",
        normalized,
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )
    logger.info("normalize_text: Normalized text: %s", normalized)
    return normalized.strip()


def tokenize(
    text: str,
) -> list[str]:

    return normalize_text(
        text
    ).split()


class ExamRAGService:

    def __init__(
        self,
        repository: ExamRepository,
    ) -> None:
        logger.info("ExamRAGService: Initializing with repository: %s", repository)

        self.exams = repository.get_all()

        corpus = [
            tokenize(exam.name)
            for exam in self.exams
        ]

        self.index = BM25Okapi(corpus)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> ExamSearchResult:
        logger.info("ExamRAGService: Searching exams with query: %s, top_k: %d", query, top_k)

        if not query.strip():
            return ExamSearchResult(
                query=query,
                matches=[],
            )

        query_tokens = tokenize(query)

        scores = self.index.get_scores(
            query_tokens
        )

        ranked = sorted(
            zip(self.exams, scores),
            key=lambda item: item[1],
            reverse=True,
        )

        matches: list[ExamMatch] = []

        for exam, score in ranked[:top_k]:

            min_score=1.5

            if score < min_score:
                continue

            matches.append(
                ExamMatch(
                    name=exam.name,
                    code=exam.code,
                    score=float(score),
                )
            )
            logger.info("ExamRAGService: Added match for exam: %s with score: %f", exam.name, score)

        return ExamSearchResult(
            query=query,
            matches=matches,
        )