# Data Pipeline & API Stack

This repository contains a Docker Compose setup for a complete data pipeline infrastructure with Dagster, PostgreSQL, MinIO, Hasura GraphQL, and a custom FastAPI service.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Git (for cloning the repository)
- Basic understanding of containerized applications

## 🚀 Quick Start

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.default .env
   ```

3. Edit the `.env` file and fill in your API keys and passwords:
   ```bash
   # Edit with your favorite text editor
   nano .env
   ```

4. Create the required directory structure:
   ```bash
   # Make sure the api directory exists
   mkdir -p api
   ```

5. Start all services:
   ```bash
   docker-compose up -d
   ```

## 🛠️ Services

The stack includes the following services:

| Service | Description | URL |
|---------|-------------|-----|
| **dagster-webserver** | Dagster UI for workflow management | http://localhost:3000 |
| **dagster-daemon** | Background service for Dagster | N/A |
| **postgres** | PostgreSQL database for all services | localhost:5432 |
| **minio** | Object storage (S3-compatible) | http://localhost:9000 (API)<br>http://localhost:9001 (Console) |
| **hasura** | GraphQL API server | http://localhost:8080 |
| **api** | Custom FastAPI service | http://localhost:8000 |

## ⚙️ Configuration

All service configuration is done through environment variables in the `.env` file:

- **Dagster settings**: Configure the pipeline orchestration
- **Qdrant settings**: For vector database connectivity
- **Postgres settings**: Database credentials and connection info
- **MinIO settings**: Object storage access credentials
- **Hasura settings**: GraphQL engine configuration
- **API settings**: Custom service settings


## 🔍 Troubleshooting

### Common Issues

1. **Docker connection errors**:
   - Make sure Docker daemon is running: `sudo systemctl start docker`
   - Check if you have permission to use Docker: `docker ps`
   - If you're using Docker Desktop, ensure it's running

2. **Missing API keys warnings**:
   - Make sure you've filled in the `.env` file with required API keys
   - Restart services after updating environment variables: `docker-compose down && docker-compose up -d`

3. **Service health check failures**:
   - Check logs for specific services: `docker-compose logs postgres`
   - Increase health check retry values in docker-compose.yml if needed

### Checking Service Status

```bash
# View all running containers
docker-compose ps

# Check logs for specific service
docker-compose logs api

# Follow logs in real-time
docker-compose logs -f dagster-webserver
```

## 🧰 Development

### Adding New Services

To add a new service:

1. Add service definition to `docker-compose.yml`
2. Connect it to the appropriate network(s)
3. Add any required environment variables to `.env.default`
4. Update this README with service details

### Modifying the FastAPI Service

The FastAPI service is mounted as a volume, so you can modify code in the `api/` directory and changes will be reflected immediately thanks to the `--reload` flag.
