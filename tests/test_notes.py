from unittest.mock import AsyncMock, MagicMock, patch

from httpx import Request, Response
import pytest

from arcade.sdk.errors import ToolExecutionError
from arcade_closeio.tools.notes import create_note


@pytest.fixture
def mock_context():
    context = AsyncMock()
    return context


@pytest.fixture
def mock_client():
    with patch("arcade_closeio.tools.notes.httpx.AsyncClient") as client:
        yield client.return_value.__aenter__.return_value


@pytest.mark.asyncio
async def test_create_note_happy_path(mock_client, mock_context) -> None:
    mock_client.post.return_value = Response(
        status_code=200,
        json={
            "id": "note_id",
            "_type": "Note",
            "note_html": "<p>Hello, world</p>",
            "note": "Hello, world",
            "attachments": [],
            "user_id": "user_id",
            "user_name": "User Name",
            "updated_by": "user_id",
            "updated_by_name": "User Name",
            "date_updated": "2024-12-11T12:00:00.000000+00:00",
            "created_by": "user_id",
            "created_by_name": "User Name",
            "organization_id": "org_id",
            "contact_id": None,
            "date_created": "2024-12-11T12:00:00.000000+00:00",
            "lead_id": "lead_id",
        },
        request=MagicMock(spec=Request),
    )

    result = await create_note(
        context=mock_context,
        lead_id="lead_id",
        note_content="<p>Hello, world</p>",
    )
    assert result == "note_id"


@pytest.mark.asyncio
async def test_create_note_http_error(mock_client, mock_context) -> None:
    mock_client.post.return_value = Response(
        status_code=429,
        json={"status": 429, "title": "Rate limit exceeded"},
        request=MagicMock(spec=Request),
    )

    with pytest.raises(ToolExecutionError):
        await create_note(
            context=mock_context,
            lead_id="lead_id",
            note_content="<p>Hello, world</p>",
        )
