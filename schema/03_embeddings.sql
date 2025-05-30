-- Tables for storing embeddings
CREATE TABLE product_embeddings (
    product_key TEXT PRIMARY KEY,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attribute_embeddings (
    attribute_key TEXT PRIMARY KEY,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE category_embeddings (
    category_key TEXT PRIMARY KEY,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE value_embeddings (
    value_key TEXT PRIMARY KEY,
    value TEXT,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
); 