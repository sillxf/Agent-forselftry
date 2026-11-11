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

## RAG Pipeline

1. Load security documents

2. Split documents into chunks

3. Generate embeddings

4. Store vectors in FAISS

5. Convert user query into embedding

6. Retrieve similar chunks

7. Return relevant security knowledge

## Example Investigation Flow
输入：
AL-001

系统：
1. Load alert

2. Calculate risk

3. Retrieve security knowledge

4. Build investigation context

5. Generate analysis

输出：
Attack:
Brute Force

Evidence:
Multiple failed login attempts

Recommendation:
Block IP
Enable MFA
Investigate account