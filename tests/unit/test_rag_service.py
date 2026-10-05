from pathlib import Path

from mcp_servers.rag.repository import (
    ExamRepository,
)
from mcp_servers.rag.service import (
    ExamRAGService,
)


def test_rag_finds_hemogram():

    repository = ExamRepository(
        Path("data/exams.json")
    )

    service = ExamRAGService(
        repository
    )

    result = service.search(
        "hemograma"
    )

    assert result.matches

    assert (
        result.matches[0].name
        == "Hemograma Completo"
    )

    assert (
        result.matches[0].code
        == "LAB001"
    )

def test_rag_normalizes_query():

    repository = ExamRepository(
        Path("data/exams.json")
    )

    service = ExamRAGService(
        repository
    )

    result = service.search(
        "GLICEMIA EM JEJUM"
    )

    assert result.matches

    assert (
        result.matches[0].name
        == "Glicemia em Jejum"
    )

def test_rag_returns_empty_for_unknown_query():

    repository = ExamRepository(
        Path("data/exams.json")
    )

    service = ExamRAGService(
        repository
    )

    result = service.search(
        "xyzabcfoobar"
    )

    assert result.matches == []