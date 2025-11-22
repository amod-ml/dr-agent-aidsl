from typing import Annotated

from fastapi import FastAPI, Form, HTTPException

from api.controllers.research_controller import run_deep_research_pipeline
from api.models import DeepResearchResponse
from api.structlogger import logger

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    logger.info("GET /")
    return {"message": "Hello! This is the root endpoint."}


@app.post("/deep-research", response_model=DeepResearchResponse)
async def deep_research(
    original_query: Annotated[str, Form(description="The user's original query")],
    source_mode: Annotated[str, Form(description="Source mode, e.g. 'web'")] = "web",
) -> DeepResearchResponse:
    """
    Execute the Deep Research Pipeline.

    Receives a query, runs planning, research, and report generation,
    and returns a Markdown report.
    """
    log = logger.bind(endpoint="/deep-research", original_query=original_query)
    log.info("Received deep research request")

    try:
        report = run_deep_research_pipeline(original_query, source_mode=source_mode)

        if report.startswith("Error:"):
            log.error("Pipeline returned error", error=report)
            raise HTTPException(status_code=500, detail=report)

        return DeepResearchResponse(report=report)
    except HTTPException:
        raise
    except NotImplementedError as e:
        log.error("Not implemented error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        log.error("Unexpected error in deep research endpoint", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error during research.") from e
