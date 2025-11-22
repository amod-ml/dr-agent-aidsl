from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from dotenv import load_dotenv

from api.controllers.query_preprocessor_controller import query_planner_agent
from api.models import ResearchBundle
from api.structlogger import logger

load_dotenv()

# --- Research Agent ---
research_agent = Agent(
    name="ResearchAgent",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[ExaTools()],
    description=("You are a thorough web researcher. Your role is to gather information using Exa search, structure it, and ensure it is high-quality."),
    instructions=[
        "You will receive an original user query and a list of 5 expanded queries.",
        "Your task is to execute a search for EACH of the 5 queries using the Exa search tool.",
        "CRITICAL: When calling the search tool, you MUST strictly use the parameter `all=True` (or equivalent boolean flag) "
        "to ensure you get full enriched results (text, summary, etc.).",
        "Process:",
        "1. Run the search for each query.",
        "2. Collect the results.",
        "3. Deduplicate sources by URL. If a high-quality source appears in multiple queries, keep the best occurrence.",
        "4. Filter out irrelevant or extremely low-quality results.",
        "5. Structure the output into the required JSON format.",
        "Do NOT try to write a prose answer. Your only output is the structured ResearchBundle.",
        "Do NOT fabricate URLs or data.",
    ],
    output_schema=ResearchBundle,
    markdown=False,
)

# --- Report Creator Agent ---
report_creator_agent = Agent(
    name="ReportCreatorAgent",
    model=OpenAIChat(id="gpt-5-mini"),
    description=(
        "You are an expert analyst and technical writer. Your goal is to synthesize "
        "structured research data into a comprehensive, detailed and readable Markdown report."
    ),
    instructions=[
        "You will receive a 'ResearchBundle' containing search results and notes.",
        "Generate a final Markdown report for the user with the following structure:",
        "Report Structure:",
        "# Summary",
        "  - Direct, concise answer to the user's question.",
        "# Detailed Analysis",
        "  - Explanations, comparisons, key concepts.",
        "  - Caveats and uncertainties.",
        "# How this was researched",
        "  - Brief methodology (Exa search, multiple queries used).",
        "  - Limitations of sources.",
        "# Sources",
        "  - Numbered list of used sources.",
        "  - Format: [N] Title - URL (Domain)",
        "  - Optional short note on why it was used.",
        "Guidelines:",
        "- Base everything strictly on the provided research bundle.",
        "- Do NOT hallucinate specific studies or URLs.",
        "- If sources disagree, acknowledge the conflict.",
        "- Use numeric references [1] in the text matching the Sources list.",
        "- The output must be pure Markdown.",
    ],
    markdown=True,
)


def run_deep_research_pipeline(original_query: str, source_mode: str = "web") -> str:
    """
    Orchestrates the Deep Research Pipeline.

    Flow:
    1. QueryPlannerAgent -> expands query into 5 queries (QueryPlan).
    2. ResearchAgent -> searches web for these queries -> ResearchBundle.
    3. ReportCreatorAgent -> synthesizes bundle into Markdown report.

    Args:
        original_query: The user's raw question.
        source_mode: "web" (default). Future extension point.

    Returns:
        Final Markdown report string.
    """
    log = logger.bind(original_query=original_query, source_mode=source_mode)
    log.info("Starting Deep Research Pipeline")

    if source_mode != "web":
        # Placeholder for future logic
        log.error("Unsupported source mode", source_mode=source_mode)
        raise NotImplementedError(f"Source mode '{source_mode}' not yet implemented.")

    # 1. Query Planning
    # We pass the original query to the planner.
    # The planner returns a QueryPlan object (validated by its output_schema).
    log.info("Executing Query Planner")
    query_plan_response = query_planner_agent.run(original_query)

    # Extract the QueryPlan object.
    # Agno's run() returns a RunResponse. .content should be the object if output_schema is set.
    query_plan = query_plan_response.content

    if not query_plan:
        log.error("Failed to generate query plan")
        return "Error: Failed to generate query plan."

    log.info("Query Plan Generated", expanded_queries=query_plan.queries)

    # 2. Research
    # Construct input for ResearchAgent
    research_input = f"Original Query: {original_query}\nExpanded Queries: {query_plan.queries}\nPlease execute the search and return the ResearchBundle."

    log.info("Executing Research Agent")
    research_response = research_agent.run(research_input)
    research_bundle = research_response.content

    if not research_bundle:
        log.error("Failed to gather research")
        return "Error: Failed to gather research."

    log.info("Research Bundle Collected", result_count=sum(len(g.items) for g in research_bundle.search_results))

    # 3. Report Generation
    # We pass the bundle (Pydantic model) directly; Agno handles serialization usually,
    # or we can pass it as a dict/string. Passing the model as context/message is best.
    # To be safe and clear, we'll convert to dict or formatted string.
    # Given the agent expects the bundle, we can just pass it in the prompt or as structured input if supported.
    # For now, we'll serialize it to JSON string to ensure the LLM reads it clearly.
    report_input = f"Here is the ResearchBundle:\n{research_bundle.model_dump_json(indent=2)}\nPlease generate the report."

    log.info("Executing Report Creator Agent")
    report_response = report_creator_agent.run(report_input)
    final_report = report_response.content

    # Ensure we return a string (Agent content can be None or other types)
    result = str(final_report) if final_report else "Error: Failed to generate report."

    log.info("Deep Research Pipeline Completed")
    return result
