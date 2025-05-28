# Development Guide

## Setup

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