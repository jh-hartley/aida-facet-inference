# Facet Inference Experimentation

(Implementation is a WIP) A product facet inference system that uses vector databases, LLMs, and tool calling to intelligently categorise and enrich product data. The system takes in product information, queries a local database for similar products, searches online for additional context when needed, and uses LLMs to infer missing filters/facets based on the gathered information. Secondarily, it attempts to indicate the confidence of each result and quantify predication accuracy using known ground truth facets.

## Initial Planned Features

- Local PostgreSQL database with pgvector for vector similarity search
- LLM-powered inference of product attributes
- FastAPI backend for programmatic access
- Streamlit interface for testing and visualisation
- Online product lookup capabilities

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aida-facet-inference.git
cd aida-facet-inference
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install the package with development dependencies:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```bash
# Database Configuration
DB_NAME=aida_db
DB_USER=aida_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432
DB_USE_SSL=false

# Database Pool Configuration (optional)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=2
DB_ASYNC_POOL_SIZE=20

# OpenAI API Configuration (required)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
```

5. Start the PostgreSQL database with pgvector:
```bash
# Start the database service
docker compose --profile db up -d

# Verify the database is running
docker ps
```

6. Test the database connection:
```bash
# Connect to the database
docker exec -it aida-pg-db psql -U aida_user -d aida_db

# Once connected, verify the vector extension is installed
\dx

# Verify the tables are created
\dt

# Exit the database
\q
```

## Usage

### Running the API Server

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Running the Streamlit Interface

```bash
streamlit run src/streamlit_app.py
```

## Development

The project uses several standard tools to maintain code quality, all managed through a single check script:

- `black` for code formatting
- `flake8` for linting
- `isort` for import sorting
- `mypy` for type checking
- `pytest` for testing

To run all checks before pushing changes:

```bash
./scripts/check.sh
```

To automatically fix formatting and import sorting issues:

```bash
./scripts/check.sh --fix
```

## Project Structure

```
aida-facet-inference/
├── src/
│   ├── api/                    # FastAPI endpoints
│   ├── core/                   # Core business logic
│   ├── db/                     # Database operations
│   └── utils/              
│   ├── config.py
│   └── streamlit_app.py
├── tests/                      
├── docs/                       
├── schema/                     # Database schema and migrations
│   └── 01_init.sql
└── docker-compose.yml          # Docker services configuration
```

## Database Schema

The system uses PostgreSQL with the pgvector extension for vector similarity search. The main tables are:

- `products`: Stores product information
- `facets`: Stores facet definitions
- `product_facets`: Junction table linking products to their facets
- `product_embeddings`: Stores vector embeddings for similarity search

See `schema/01_init.sql` for the complete schema definition.