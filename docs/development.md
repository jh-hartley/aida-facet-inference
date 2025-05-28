# Development Guide

## Development Approaches

### Local Development (Recommended)

This approach is recommended for active development as it provides:
- Fast iteration with hot-reloading
- Direct access to the codebase
- Quick testing of changes
- Better debugging capabilities

#### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aida-facet-inference.git
cd aida-facet-inference
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Start the database (using Docker):
```bash
docker-compose up db
```

6. Run the API with hot-reloading:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables hot-reloading, so your API will automatically update when you make code changes.

### Docker-based Development

This approach is useful for:
- Testing the production-like environment
- Ensuring consistency across team members
- CI/CD pipeline testing

#### Setup

1. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

2. Start services:
```bash
# Start both API and database
docker-compose up

# Or start individual services
docker-compose up db    # Just the database
docker-compose up api   # Just the API
```

Note: Code changes require rebuilding the container, which is slower for active development.

## Code Quality

The project uses several tools to maintain code quality:

- `black` for code formatting
- `flake8` for linting
- `isort` for import sorting
- `mypy` for type checking
- `pytest` for testing

### Running Checks

```bash
# Run all checks
./scripts/check.sh

# Fix formatting issues
./scripts/check.sh --fix
```

### Type Checking

The project uses strict type checking. Run mypy:

```bash
mypy src/
```

### Testing

Run tests with pytest:

```bash
pytest
```

## Project Structure

```
src/
├── api/                    # FastAPI endpoints
├── core/                   # Core business logic
│   ├── facet_inference/    # Facet inference implementation
│   └── llm/                # LLM integration
├── db/                     # Database operations
└── utils/                  # Utility functions
```

## Adding New Features

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Run all checks:
```bash
./scripts/check.sh
```

4. Create a pull request

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run all checks
5. Submit a pull request

## Best Practices

1. **Type Annotations**
   - Use type hints for all function parameters and return values
   - Use `Optional` for nullable values
   - Use `Sequence` instead of `list` for read-only sequences

2. **Async Code**
   - Use `async/await` for I/O operations
   - Use `gather` for concurrent operations
   - Handle exceptions appropriately

3. **Documentation**
   - Add docstrings to all public functions and classes
   - Update documentation when changing APIs
   - Include examples in docstrings

4. **Testing**
   - Write tests for new features
   - Maintain test coverage
   - Use fixtures for common setup

5. **Code Style**
   - Follow PEP 8
   - Use meaningful variable names
   - Keep functions small and focused

6. **Development Workflow**
   - Use local development for active coding
   - Test in Docker before committing
   - Keep the database schema in sync
   - Document any new environment variables 