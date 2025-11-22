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


class ResearchResultItem(BaseModel):
    url: str
    title: str
    snippet: str
    score: float | None = None
    published_at: str | None = None
    source_type: str = "web"


class ResearchResultGroup(BaseModel):
    query: str
    engine: str = "exa"
    items: list[ResearchResultItem]


class ResearchNote(BaseModel):
    id: str
    query: str
    source_url: str
    summary: str
    stance: str
    quality_hint: str


class ResearchBundle(BaseModel):
    original_query: str
    expanded_queries: list[str]
    search_results: list[ResearchResultGroup]
    research_notes: list[ResearchNote] | None = None


class DeepResearchResponse(BaseModel):
    report: str
