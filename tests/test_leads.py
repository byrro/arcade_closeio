from unittest.mock import AsyncMock, MagicMock, patch

from httpx import Request, Response
import pytest

from arcade.sdk.errors import ToolExecutionError
from arcade_closeio.tools.leads import search_leads_by_url


@pytest.fixture
def mock_context():
    context = AsyncMock()
    return context


@pytest.fixture
def mock_client():
    with patch("arcade_closeio.tools.notes.httpx.AsyncClient") as client:
        yield client.return_value.__aenter__.return_value


@pytest.mark.asyncio
async def test_search_leads_by_url_happy_path(mock_client, mock_context) -> None:
    mock_client.post.return_value = Response(
        status_code=200,
        json={
            "data": [
                {
                    "__object_type": "lead",
                    "id": "mock_lead_id_1",
                },
                {
                    "__object_type": "lead",
                    "id": "mock_lead_id_2",
                },
                {
                    "__object_type": "lead",
                    "id": "mock_lead_id_3",
                },
            ],
            "cursor": None,
        },
        request=MagicMock(spec=Request),
    )

    result = await search_leads_by_url(
        context=mock_context,
        url="acme.com",
        limit=5,
    )
    assert result == ["mock_lead_id_1", "mock_lead_id_2", "mock_lead_id_3"]


@pytest.mark.asyncio
async def test_search_leads_by_url_http_error(mock_client, mock_context) -> None:
    mock_client.post.return_value = Response(
        status_code=429,
        json={"status": 429, "title": "Rate limit exceeded"},
        request=MagicMock(spec=Request),
    )

    with pytest.raises(ToolExecutionError):
        await search_leads_by_url(
            context=mock_context,
            url="acme.com",
            limit=3,
        )
