from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello! This is the root endpoint."}


@patch("api.main.run_deep_research_pipeline")
def test_deep_research_endpoint_success(mock_pipeline):
    # Setup mock
    mock_pipeline.return_value = "# Final Report\n\nResult."

    # Execute request
    response = client.post("/deep-research", data={"original_query": "Test query", "source_mode": "web"})

    # Verify
    assert response.status_code == 200
    assert response.json() == {"report": "# Final Report\n\nResult."}
    mock_pipeline.assert_called_once_with("Test query", source_mode="web")


@patch("api.main.run_deep_research_pipeline")
def test_deep_research_endpoint_error(mock_pipeline):
    # Setup mock to fail
    mock_pipeline.return_value = "Error: Something went wrong."

    # Execute request
    response = client.post("/deep-research", data={"original_query": "Test query"})

    # Verify
    assert response.status_code == 500
    assert "Something went wrong" in response.json()["detail"]
