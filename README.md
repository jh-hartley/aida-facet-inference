# AIDA Facet Inference

A product facet inference system that uses LLMs to intelligently categorise and enrich product data. The system takes in product information and uses LLMs to infer missing facets based on the gathered information, with confidence scoring and validation.

## Quick Start

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

3. Run the API:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
aida-facet-inference/
├── src/
│   ├── api/                    # FastAPI endpoints
│   ├── core/                   # Core business logic
│   │   ├── facet_inference/    # Facet inference implementation
│   │   └── llm/                # LLM integration
│   ├── db/                     # Database operations
│   └── utils/                  # Utility functions
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