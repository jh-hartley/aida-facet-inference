# AIDA Facet Inference

A product facet inference system that uses LLMs to intelligently categorise and enrich product data. The system takes in product information and uses LLMs to infer missing facets based on the gathered information, with confidence scoring and validation.

## Development Setup

### Local Development (Recommended for Active Development)

This setup is ideal for development as it allows for quick code changes and testing without rebuilding containers.

1. Clone and install:
```bash
git clone https://github.com/yourusername/aida-facet-inference.git
cd aida-facet-inference
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e ".[dev]"
```

2. Configure environment:
```bash
# Copy example env file
cp .env.example .env
# Edit .env with your settings
```

3. Start the database (using Docker):
```bash
docker-compose --profile db up
```

4. Run the API locally:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables hot-reloading, so your API will automatically update when you make code changes.

### Docker-based Development

For Docker-based development, you have several options:

1. Run services separately (recommended for development):
```bash
# Terminal 1 - Start the database
docker-compose --profile db up

# Terminal 2 - Start the API
docker-compose --profile api up
```

2. Run everything together (useful for testing the full stack):
```bash
docker-compose --profile all up
```

Note: When running services separately, the API will start even if the database isn't ready. This is intentional for development purposes. The API will handle database connection retries internally.

The separate service approach allows you to:
- See logs clearly for each service
- Stop and restart services independently
- Quickly identify which service has issues
- Maintain separate terminal windows for each service's logs

Note: The Docker-based approach requires rebuilding the container for code changes, which is slower for active development.

## Project Structure

```
aida-facet-inference/
├── src/
│   ├── api/                    # FastAPI endpoints
│   ├── core/                   # Core business logic
│   │   ├── facet_inference/    # Facet inference implementation
│   │   └── llm/                # LLM integration
│   ├── db/                     # Database operations
│   ├── utils/                  # Utility functions
│   └── main.py                 # Application entry point
├── tests/                      # Test suite
├── docs/                       # Detailed documentation
└── scripts/                    # Utility scripts
```

## Documentation

- [Core Concepts](docs/core_concepts.md) - Overview of facet inference concepts
- [API Reference](docs/api_reference.md) - Detailed API documentation
- [Development Guide](docs/development.md) - Setup and contribution guidelines
- [Architecture](docs/architecture.md) - System architecture and design decisions

## Development

```bash
# Run all checks
./scripts/check.sh

# Fix formatting issues
./scripts/check.sh --fix
```