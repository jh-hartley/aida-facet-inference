CREATE TABLE retailers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    is_client BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    identifier_value TEXT NOT NULL,  -- EAN/GTIN
    identifier_type TEXT NOT NULL,   -- 'EAN', 'UPC', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(identifier_value, identifier_type)
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    retailer_id INTEGER REFERENCES retailers(id),
    parent_id INTEGER REFERENCES categories(id),
    name TEXT NOT NULL,
    system_name TEXT,  -- Original category path from retailer
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(retailer_id, system_name)
);

-- Facet definitions
CREATE TABLE facets (
    id SERIAL PRIMARY KEY,
    retailer_id INTEGER REFERENCES retailers(id),
    name TEXT NOT NULL,
    description TEXT,
    attribute_type TEXT,  -- e.g., 'numeric', 'categorical', 'boolean'
    unit_measure_type TEXT,  -- e.g., 'CM', 'KG'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(retailer_id, name)
);

CREATE TABLE facet_allowed_values (
    id SERIAL PRIMARY KEY,
    facet_id INTEGER REFERENCES facets(id),
    value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(facet_id, value)
);

CREATE TABLE category_facets (
    category_id INTEGER REFERENCES categories(id),
    facet_id INTEGER REFERENCES facets(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (category_id, facet_id)
);

CREATE TABLE product_metadata (
    id SERIAL PRIMARY KEY,
    retailer_id INTEGER REFERENCES retailers(id),
    product_id INTEGER REFERENCES products(id),
    facet_id INTEGER REFERENCES facets(id),
    value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(retailer_id, product_id, facet_id)
);

CREATE TABLE product_embeddings (
    id SERIAL PRIMARY KEY,
    retailer_id INTEGER REFERENCES retailers(id),
    product_id INTEGER REFERENCES products(id),
    embedding_model TEXT NOT NULL,  -- e.g., 'openai-ada-002'
    embedding vector(1536),  -- Adjust dimension based on model
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(retailer_id, product_id, embedding_model)
);

CREATE TABLE facet_predictions (
    id SERIAL PRIMARY KEY,
    retailer_id INTEGER REFERENCES retailers(id),
    product_id INTEGER REFERENCES products(id),
    facet_id INTEGER REFERENCES facets(id),
    predicted_value TEXT NOT NULL,
    confidence FLOAT,
    model_version TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(retailer_id, product_id, facet_id, model_version)
);