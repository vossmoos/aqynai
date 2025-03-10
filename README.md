# Aqyn AI

This is a preconfigured set of applications for RAG (Retrieval-Augmented Generation) systems implementation. The main components include:

- **Dagster**: Handles preprocessing of data and manages data pipelines.
- **Qdrant**: Vector database for storing embeddings.
- **Langflow**: Enables creating AI agent flows.
- **MinIO**: Acts as an object storage solution for data persistence.

## Services

### Creating Agent Flows (Langflow)
Langflow enables the creation of agent flows for AI pipelines. It depends on Qdrant, Dagster, and MinIO for storing and managing embeddings and data.

### Qdrant
Qdrant is a vector database optimized for similarity search and storing embeddings.

### Dagster Webserver
Dagster is used for orchestrating preprocessing workflows. It manages and schedules data processing tasks.

### Dagster Daemon
The Dagster Daemon service is responsible for running background tasks and scheduled jobs.

### MinIO
MinIO is a high-performance, distributed object storage system used for data persistence.

## Volumes

- `data_volume`: Stores Qdrant and Langflow data.
- `dagster_home1`: Stores Dagster-related configuration and workflow data.

## Usage

To start the services, run:
```sh
docker-compose up -d
```

To stop the services:
```sh
docker-compose down
```

## Dependencies
- Docker Compose 3.9+
- Python (for Dagster-related configurations)

## Architecture Overview
1. **Dagster** preprocesses data and generates embeddings.
2. **Qdrant** stores the embeddings for retrieval.
3. **Langflow** enables creating AI agent flows.
4. **MinIO** stores additional data required for processing.

This setup ensures a streamlined workflow for managing data pipelines, embeddings, and AI-driven applications.

