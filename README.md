# AI-SecOps-Agent

An AI-assisted security alert investigation system.

## Current features

- Security alert data model
- List and filter alerts by severity
- Retrieve a single alert by ID
- HTTP API tests

## Setup

Create and activate a Python virtual environment, then run:

    python -m pip install -r requirements.txt

## Start the application

    uvicorn app.main:app --reload

## Run tests

    pytest -q

## API documentation

Open http://127.0.0.1:8000/docs

## Roadmap

- Alert normalization and deduplication
- Asset and event investigation tools
- Retrieval-augmented generation
- Agent tool calling
- Workflow and ReAct comparison
- Evaluation and observability