from arcade.sdk import ToolCatalog
from arcade.sdk.eval import (
    BinaryCritic,
    EvalRubric,
    EvalSuite,
    tool_eval,
)

import arcade_closeio
from arcade_closeio.tools.leads import search_leads_by_url

# Evaluation rubric
rubric = EvalRubric(
    fail_threshold=0.90,
    warn_threshold=0.95,
)


catalog = ToolCatalog()
catalog.add_module(arcade_closeio)


@tool_eval()
def closeio_eval_suite() -> EvalSuite:
    suite = EvalSuite(
        name="Close.io leads tool evaluation",
        system_message=(
            "You are an AI assistant with access to tools that can interact with "
            "the Close.io CRM API. The tools are designed to help users manage their "
            "Close.io account by performing various tasks such as searching for leads."
        ),
        catalog=catalog,
        rubric=rubric,
    )

    suite.add_case(
        name="Search leads by url on Close.io",
        user_message=(
            "Get the lead id for the URL 'acme.com' on Close.io"
        ),
        expected_tool_calls=[
            (search_leads_by_url, {"url": "acme.com", "limit": 1}),
        ],
        rubric=rubric,
        critics=[
            BinaryCritic(critic_field="url", weight=0.9),
            BinaryCritic(critic_field="limit", weight=0.1),
        ],
    )

    return suite
