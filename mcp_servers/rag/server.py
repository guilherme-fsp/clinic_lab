from pathlib import Path

from mcp.server import MCPServer

from mcp_servers.rag.repository import ExamRepository
from mcp_servers.rag.schemas import ExamSearchResult
from mcp_servers.rag.service import ExamRAGService

DATA_PATH = Path("data/exams.json")

repository = ExamRepository(DATA_PATH)

rag_service = ExamRAGService(repository)

mcp = MCPServer("laboratory-exam-rag-server")

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

@mcp.tool()

def search_exams(query: str, top_k: int = 5) -> ExamSearchResult:
    """
    Search the fictitious laboratory exam
    knowledge base and return the most
    relevant exams with their codes.
    """
    logger.info("search_exams: Searching exams with query: %s, top_k: %d", query, top_k)

    return rag_service.search(
        query=query,
        top_k=top_k,
    )

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8002,
        sse_path="/sse"
    )
