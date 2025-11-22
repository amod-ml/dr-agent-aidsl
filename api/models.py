from pydantic import BaseModel, Field


class QueryPlan(BaseModel):
    """Structured output for query preprocessor agent.

    Contains exactly 5 queries: 3 related queries and 2 decomposition queries.
    """

    queries: list[str] = Field(
        min_length=5,
        max_length=5,
        description="Exactly 5 search queries: first 3 are related queries, last 2 are decomposition queries",
    )

