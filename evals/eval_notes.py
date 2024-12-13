from arcade.sdk import ToolCatalog
from arcade.sdk.eval import (
    BinaryCritic,
    EvalRubric,
    EvalSuite,
    tool_eval,
)

import arcade_closeio
from arcade_closeio.tools.notes import create_note_for_lead

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
        name="Close.io notes tool evaluation",
        system_message=(
            "You are an AI assistant with access to tools that can interact with "
            "the Close.io CRM API. The tools are designed to help users manage their "
            "Close.io account by performing various tasks such as creating notes "
            "about leads."
        ),
        catalog=catalog,
        rubric=rubric,
    )

    suite.add_case(
        name="Create note for a lead on Close.io",
        user_message=(
            "Create a note on Close.io for the lead id '123abcX': 'quick brown fox'"
        ),
        expected_tool_calls=[
            (create_note_for_lead, {"lead_id": "123abcX", "note_content": "quick brown fox"}),
        ],
        rubric=rubric,
        critics=[
            BinaryCritic(critic_field="lead_id", weight=0.5),
            BinaryCritic(critic_field="note_content", weight=0.5),
        ],
    )

    return suite
