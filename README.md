# Lead Qualification API

Backend service for managing inbound leads, running AI-assisted lead scoring, and controlling handoff to sales through explicit business rules.

This project demonstrates:
- asynchronous API development with FastAPI
- PostgreSQL integration with Tortoise ORM
- separation of API, business logic, and AI/scoring logic
- controlled AI usage in a product workflow

---

## Overview

The service models a simplified lead-processing workflow.

A lead moves through a cold pipeline, can be analyzed by an AI-assisted scoring module, and may be transferred to sales only if specific business conditions are met.

The goal of the project is to show how AI can be integrated into a backend system as a **decision-support component**, not as a fully autonomous mechanism.

---

## Key Features

- create and retrieve leads
- manage lead stages with transition validation
- run AI-assisted lead scoring
- generate a recommendation for the next step
- validate handoff to sales
- automatically create a `Sale` record on successful transfer

---

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- Tortoise ORM
- Docker / Docker Compose

---

## Business Rules

### Lead Pipeline

A cold lead moves through the following stages:

```text
new → contacted → qualified → transferred
                           ↘ lost
```

### Stage Transition Rules

- stage skipping is not allowed
- a lead can be moved to `lost` from any non-final stage
- final stages (`transferred`, `lost`) are immutable

### Sales Handoff Rules

A lead can be moved to `transferred` only if:

- `ai_score >= 0.6`
- `business_domain` is defined

If the conditions are met:
- the lead stage becomes `transferred`
- a `Sale` record is created

Otherwise, the API returns an error.

---

## AI-Assisted Scoring

The AI/scoring module analyzes a lead using:

- `source`
- `stage`
- `activity_count`
- `business_domain`

It returns:

- `score` — estimated probability of a successful deal
- `recommendation` — recommended next action
- `reason` — short explanation of the result

Example response:

```json
{
  "score": 0.78,
  "recommendation": "transfer_to_sales",
  "reason": "lead has high activity and clear business domain"
}
```

### Why AI Does Not Make the Final Decision

In this project, AI is used as an assistive module:
- it evaluates the lead
- suggests the next step
- supports the manager's decision-making

Final control remains with the system's business rules and user actions. This keeps the workflow deterministic and prevents AI from autonomously making critical product decisions.

---

## API Overview

Main endpoints:

- `POST /leads/` — create a lead
- `GET /leads/{id}` — get a lead by ID
- `PATCH /leads/{id}/stage` — update the lead stage
- `POST /leads/{id}/analyze` — run AI analysis for a lead

After startup, the API documentation is available at:

- `http://localhost:8000/docs`

---

## Project Structure

```text
app/
  api/
    leads.py
  services/
    ai_service.py
    lead_service.py
  models.py
  schemas.py
  main.py
```

### Responsibility by Layer

- `app/api/leads.py` — HTTP API and request handling
- `app/services/lead_service.py` — lead and sales business logic
- `app/services/ai_service.py` — AI/scoring module
- `app/models.py` — ORM models
- `app/schemas.py` — Pydantic schemas
- `app/main.py` — application entry point and initialization

---

## Run with Docker Compose

Requirements:
- Docker
- Docker Compose

```bash
git clone https://github.com/machinatororis/lead-ai-crm.git
cd lead-ai-crm
docker compose up --build
```

After startup:

- API: `http://localhost:8000`
- Healthcheck: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`

Services:
- `db` — PostgreSQL
- `app` — FastAPI application

---

## Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/machinatororis/lead-ai-crm.git
cd lead-ai-crm
```

### 2. Start PostgreSQL

For example, with Docker:

```bash
docker run --name lead-db \
  -e POSTGRES_DB=lead_ai_crm \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:16
```

### 3. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Example:

```env
DB_URL=postgres://postgres:postgres@localhost:5432/lead_ai_crm
```

### 4. Install Dependencies and Run the App

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

Then install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

After startup:

- Healthcheck: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`

---

## Main Entities

### Lead

Fields:
- `source` — lead source (`scanner`, `partner`, `manual`)
- `stage` — current lead stage
- `business_domain` — business domain
- `activity_count` — number of interactions
- `ai_score` — estimated deal probability
- `ai_recommendation` — AI recommendation
- `ai_reason` — explanation of the AI result

### Sale

Created automatically when a lead is successfully transferred to sales.

---

## Example Workflow

1. A manager creates a new lead  
2. The lead moves through the early stages of the cold pipeline  
3. The user runs AI analysis  
4. The system stores `score`, `recommendation`, and `reason`  
5. On transfer attempt, the service validates the business conditions  
6. If the conditions are met, a `Sale` record is created

---

## Production Considerations

In a production-ready version, I would extend the project with:

- database migrations
- automated tests for the service layer and business rules
- centralized configuration management
- structured logging and metrics
- more granular error handling
- background jobs or queues for AI analysis
- authentication and role-based access control
- external AI/ML integration instead of rule-based scoring

---

## Project Focus

This project focuses on backend design for a lead qualification workflow where AI is integrated into a clear business process and constrained by explicit system rules.

The main engineering goals were:
- separating API, business logic, and AI logic
- modeling domain constraints
- validating stage transitions
- using AI in a controlled, product-oriented way

## Tests

The project includes:
- unit tests for lead stage transition rules and sales handoff validation
- async tests for database-backed service operations
- tests for AI scoring behavior

Run tests with:

```bash
pytest