# BFF Service (Backend-For-Frontend)

The BFF API sits between the frontend React application and the ClickHouse analytics database. Its primary role is to serve structured observability metrics to populate the UI dashboard without exposing direct database queries to the client.

## API Endpoints

- `GET /api/metrics/summary`  
  Calculates and returns highly aggregated analytics:
  - Total requests processed.
  - Overall average latency.
  - Total cumulative platform cost estimated in USD.

- `GET /api/traces`
  Retrieves a paginated list of recent proxy requests.
  - `?limit=<int>` - Items per page.
  - `?offset=<int>` - Results to skip.

- `GET /health`  
  Checks if the BFF service is accepting requests (`{"status": "ok"}`).

## Data Retrieval

This service issues high-performance OLAP queries to ClickHouse. By keeping read operations constrained to this microservice, it encapsulates database logic away from frontend views and secures backend connections natively.

## Development

Access the API dynamically at port `8001` (`http://localhost:8001`). Run with the greater application suite via the root `docker-compose.yml`. Please refer to the root `README.md` for complete build instructions.
