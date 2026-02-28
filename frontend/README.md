# LLM Observability Frontend Board

The frontend provides the main User Interface for the entire LLM Observability Platform. It displays a real-time comprehensive view of the LLM application's health, metrics, and individual proxy traces.

## Core Features

- **Metrics Displays:** Visualizes key performance and cost metrics fetched directly from the `bff_service` (Backend-For-Frontend).
- **Traces Table:** Lists a chronological breakdown of the traces passing through the proxy. Provides insight into original vs. redacted prompts, cost, tokens, and trace IDs.

## Tech Stack
- Constructed with modern **React** tools.
- Uses **Vite** for rapid bundling and hot module replacement. 

## Development

During unified platform deployment, this interface relies directly on the `bff_service` API.
Available on port `3000` (`http://localhost:3000`).

To run the environment, see the initialization instructions outlined in the root `.README.md`.
