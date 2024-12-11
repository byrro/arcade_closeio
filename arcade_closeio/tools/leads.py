from typing import Annotated, Optional

import httpx

from arcade.sdk import ToolContext, tool
from arcade.sdk.errors import ToolExecutionError
from arcade_closeio.tools.utils import get_headers, get_url


def generate_url_variations(url: str) -> list[str]:
    """Generate different variations of the given URL.

    Close.io API doesn't support matching sub-strings in the URL field, so we need to
    search for the exact URL and possible common variations (with & without http/https
    protocol and www subdomain) to increase the chances of finding the lead.
    """
    base_url = url.strip().lstrip("http://").lstrip("https://").lstrip("www.")

    return [
        f"http://{base_url}",
        f"https://{base_url}",
        f"http://www.{base_url}",
        f"https://www.{base_url}",
        base_url,
    ]


@tool
async def search_leads_by_url(
    context: ToolContext,
    url: Annotated[str, "The URL to search for"],
    limit: Annotated[Optional[int], "The maximum number of leads to return"] = None,
) -> Annotated[list[str], "A list of lead ids in Close.io matching the url"]:
    """Search for leads in Close.io by the URL address"""
    url_variations = generate_url_variations(url)

    # closeio_api SDK doesn't support async requests, so we use httpx instead
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=get_url("data/search/"),
                headers=get_headers(),
                data={
                    "limit": limit,
                    "results_limit": limit,
                    "sort": [],
                    "query": {
                        "negate": False,
                        "type": "and",
                        "queries": [
                            {
                                "type": "object_type",
                                "object_type": "lead",
                                "negate": False,
                            },
                            {
                                "type": "or",
                                "negate": False,
                                "queries": [
                                    {
                                        "type": "and",
                                        "negate": False,
                                        "queries": [
                                            {
                                                "type": "field_condition",
                                                "negate": False,
                                                "condition": {
                                                    "type": "text",
                                                    "mode": "full_words",
                                                    "value": url_variation,
                                                },
                                                "field": {
                                                    "type": "regular_field",
                                                    "field_name": "url",
                                                    "object_type": "lead",
                                                },
                                            }
                                            for url_variation in url_variations
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                },
                auth=(context.authorization.token, ""),
            )
            response.raise_for_status()
            leads: list[str] = [lead["id"] for lead in response.json()["data"]]
            return leads

        except httpx.RequestError as e:
            raise ToolExecutionError(f"Failed to get create Close.io note: {e}") from e
