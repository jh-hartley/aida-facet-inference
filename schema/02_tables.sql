CREATE TABLE IF NOT EXISTS retailers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    country TEXT,
    industry TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    identifier_value TEXT NOT NULL,
    identifier_type TEXT NOT NULL,  -- 'EAN', 'UPC', 'ISBN', etc.
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    attributes JSONB,  -- Flexible schema for different product types
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_embeddings (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    embedding_model TEXT NOT NULL,  -- e.g., 'openai-ada-002', 'cohere-embed'
    embedding vector(1536),  -- must be calibrated with embedding_model
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS retailer_facets (
    id SERIAL PRIMARY KEY,
    retailer_id INTEGER REFERENCES retailers(id),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS retailer_products (
    id SERIAL,
    retailer_id INTEGER REFERENCES retailers(id),
    product_id INTEGER REFERENCES products(id),
    retailer_product_id TEXT,  -- Retailer's internal ID
    url TEXT,
    price DECIMAL,
    availability BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (retailer_id, id)
) PARTITION BY LIST (retailer_id);

CREATE TABLE IF NOT EXISTS retailer_product_attributes (
    retailer_product_id INTEGER,
    retailer_id INTEGER,
    attribute_name TEXT NOT NULL,
    attribute_value TEXT NOT NULL,
    attribute_type TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (retailer_id, retailer_product_id, attribute_name),
    FOREIGN KEY (retailer_id, retailer_product_id) 
        REFERENCES retailer_products(retailer_id, id)
) PARTITION BY LIST (retailer_id);

CREATE TABLE IF NOT EXISTS attribute_mappings (
    id SERIAL PRIMARY KEY,
    retailer_id INTEGER REFERENCES retailers(id),
    source_attribute TEXT NOT NULL,
    normalized_attribute TEXT NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(retailer_id, source_attribute)
); 