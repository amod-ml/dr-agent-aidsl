from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.models import QueryPlan, ResearchBundle, ResearchResultGroup, ResearchResultItem

client = TestClient(app)


# We mock the agents to test the orchestration logic without calling external APIs
@pytest.fixture
def mock_agents():
    with (
        patch("api.controllers.research_controller.query_planner_agent") as mock_planner,
        patch("api.controllers.research_controller.research_agent") as mock_research,
        patch("api.controllers.research_controller.report_creator_agent") as mock_report,
    ):
        # Setup Query Planner Response
        mock_plan = QueryPlan(queries=["q1", "q2", "q3", "d1", "d2"])
        mock_planner.run.return_value.content = mock_plan

        # Setup Research Response
        mock_bundle = ResearchBundle(
            original_query="test",
            expanded_queries=["q1", "q2", "q3", "d1", "d2"],
            search_results=[ResearchResultGroup(query="q1", items=[ResearchResultItem(url="http://test.com", title="Test", snippet="Snippet")])],
        )
        mock_research.run.return_value.content = mock_bundle

        # Setup Report Response
        mock_report.run.return_value.content = "# Integration Report"

        yield mock_planner, mock_research, mock_report


def test_deep_research_flow_integration(mock_agents):
    """
    Tests the full flow from API -> Controller -> Agents (mocked) -> API Response.
    This ensures all data models and passing logic works correctly.
    """
    response = client.post("/deep-research", data={"original_query": "Integration Test Query"})

    assert response.status_code == 200
    assert response.json()["report"] == "# Integration Report"

    # Verify agent calls
    mock_planner, mock_research, mock_report = mock_agents

    # Planner called with query
    mock_planner.run.assert_called()

    # Research called with formatted string containing expanded queries
    research_call_arg = mock_research.run.call_args[0][0]
    assert "Integration Test Query" in research_call_arg
    assert "q1" in research_call_arg

    # Report called with JSON dump of bundle
    report_call_arg = mock_report.run.call_args[0][0]
    assert "ResearchBundle" in report_call_arg
    assert "http://test.com" in report_call_arg
