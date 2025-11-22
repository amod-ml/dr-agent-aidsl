import sys
from pathlib import Path

import structlog

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from api import structlogger  # noqa: F401
from api.controllers.query_preprocessor_controller import query_planner_agent
from api.models import QueryPlan

logger = structlog.get_logger()

EXPECTED_QUERY_COUNT = 5
RELATED_QUERIES_COUNT = 3
DECOMPOSITION_QUERIES_COUNT = 2


def test_query_preprocessor() -> None:
    response = query_planner_agent.run("Explain how diffusion models work in image generation and compare them to GANs.")
    # With output_schema, response.content is a QueryPlan instance
    query_plan: QueryPlan = response.content
    logger.info(
        "Query preprocessor response",
        queries=query_plan.queries,
        related_queries=query_plan.queries[:RELATED_QUERIES_COUNT],
        decomposition_queries=query_plan.queries[RELATED_QUERIES_COUNT:],
    )
    # Validate structure
    assert query_plan is not None
    assert isinstance(query_plan, QueryPlan)
    assert len(query_plan.queries) == EXPECTED_QUERY_COUNT
    assert all(isinstance(query, str) for query in query_plan.queries)
    # Validate structure: 3 related + 2 decomposition
    assert len(query_plan.queries[:RELATED_QUERIES_COUNT]) == RELATED_QUERIES_COUNT, "First 3 queries should be related queries"
    assert len(query_plan.queries[RELATED_QUERIES_COUNT:]) == DECOMPOSITION_QUERIES_COUNT, "Last 2 queries should be decomposition queries"


if __name__ == "__main__":
    test_query_preprocessor()
