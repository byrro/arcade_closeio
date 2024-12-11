from typing import Annotated

import httpx

from arcade.sdk import ToolContext, tool
from arcade.sdk.errors import ToolExecutionError
from arcade_closeio.tools.utils import get_headers, get_url


@tool
async def create_note(
    context: ToolContext,
    lead_id: Annotated[str, "The lead id in Close.io"],
    note_content: Annotated[str, "Note content (accepts HTML)"],
) -> Annotated[str, "The note id in Close.io"]:
    """Create a note associated to a lead in Close.io"""
    # closeio_api SDK doesn't support async requests, so we use httpx instead
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=get_url("/activity/note"),
                headers=get_headers(),
                data={
                    "lead_id": lead_id,
                    "note_html": note_content,
                },
                auth=(context.authorization.token, ""),
            )
            response.raise_for_status()
            note_id: str = response.json()["id"]
            return note_id

        except httpx.RequestError as e:
            raise ToolExecutionError(f"Failed to get create Close.io note: {e}") from e
