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

-- Added for similarity search views
CREATE TABLE product_attribute_embeddings (
    product_key TEXT,
    attribute_key TEXT,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_key, attribute_key)
);

CREATE TABLE product_category_embeddings (
    product_key TEXT,
    category_key TEXT,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_key, category_key)
); 