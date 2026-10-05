import pytest

from mcp import ClientSession
from mcp.client.sse import sse_client


RAG_MCP_URL = (
    "http://localhost:8002/sse"
)


@pytest.mark.anyio
async def test_rag_mcp_searches_exam():

    async with sse_client(
        RAG_MCP_URL
    ) as streams:

        read_stream, write_stream = streams

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            tools = await session.list_tools()

            assert "search_exams" in {
                tool.name
                for tool in tools.tools
            }

            result = await session.call_tool(
                "search_exams",
                arguments={
                    "query": "Hemograma Completo",
                    "top_k": 3,
                },
            )

            assert not result.is_error

            structured = (
                result.structured_content
            )

            assert structured is not None

            assert structured["matches"]

            first_match = (
                structured["matches"][0]
            )

            assert (
                first_match["name"]
                == "Hemograma Completo"
            )

            assert (
                first_match["code"]
                == "LAB001"
            )