# Wind Forecast Dashboard

Full-stack dashboard for comparing selected wind forecasts with actual wind generation.

## Run locally

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend, in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Swagger is available at `http://localhost:8000/docs`.

## API

```text
GET /api/dashboard?decision_date=2026-01-11&cutoff=10:00
```

The API loads the JSON data, filters forecasts published before the cutoff, selects the latest eligible forecast for each start time, matches it to actual wind generation, and calculates error and accuracy.

## Tests

```bash
cd backend
pytest
```

## Run with Docker

Install Docker Desktop, then run from the project root:

```bash
docker compose up --build
```

Open the dashboard at `http://localhost:5173` and the API documentation at `http://localhost:8000/docs`.

Stop the containers with:

```bash
docker compose down
```

## Submission demo

Record an unlisted video under ten minutes: first show the dashboard as a customer, then explain the architecture, data-selection logic, API, frontend, tests, and how to run the project.
