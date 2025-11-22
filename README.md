# Deep Research Agent

<div align="center">

![Python](https://img.shields.io/badge/language-python-blue?style=for-the-badge&logo=python)
![Python Version](https://img.shields.io/badge/python-3.14-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

</div>

## Overview

The **Deep Research Agent** is an autonomous web research pipeline built with **Agno** and **ExaSearch**. It takes a user query, plans a research strategy, executes parallel web searches, and synthesizes a comprehensive Markdown report.

The system is exposed via a FastAPI endpoint for easy integration.

## 🚀 Setup & Installation

This project uses **[uv](https://github.com/astral-sh/uv)** for fast package management.

### Prerequisites
- Python 3.14+
- `uv` installed
- OpenAI API Key
- Exa API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd dr-agent-aidsl
    ```

2.  **Set up environment variables:**
    Copy `env-example.txt` to `.env` and fill in your keys.
    ```bash
    cp env-example.txt .env
    ```
    Ensure you have:
    - `OPENAI_API_KEY`
    - `EXA_API_KEY`

3.  **Install dependencies:**
    ```bash
    uv sync
    ```

## 🏃‍♂️ Running the Server

Start the FastAPI development server:

```bash
uv run fastapi dev api/main.py
```

The server will start at `http://127.0.0.1:8000`.

## 🔌 API Usage

### Deep Research Endpoint

**URL**: `/deep-research`
**Method**: `POST`
**Content-Type**: `multipart/form-data`

#### Parameters

| Name             | Type     | Required | Description |
|------------------|----------|----------|-------------|
| `original_query` | `string` | Yes      | The main question or topic you want to research. |
| `source_mode`    | `string` | No       | Source filter. Defaults to `"web"`. |

#### Example Request (cURL)

```bash
curl -X POST "http://127.0.0.1:8000/deep-research" \
     -F "original_query=What is the current state of Quantum Computing in 2025?" \
     -F "source_mode=web"
```

#### Example Response

```json
{
  "report": "# Quantum Computing State of the Art 2025\n\n## Summary\nQuantum computing in 2025 has reached..."
}
```

## 🧪 Testing

### Run Tests
To run all unit and integration tests:

```bash
uv run pytest
```

### Verify API (End-to-End)
To run a real query against the running local server:

```bash
uv run python scripts/verify_api_query.py
```

---
*Built with [Agno](https://github.com/agno-agi/agno) and [Exa](https://exa.ai).*

