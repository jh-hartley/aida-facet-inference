# Database Schema

## Overview

The project uses a PostgreSQL database with the following key tables:

## Core Tables

### Retailers
Stores information about retailers whose products we process.
- `id`: Unique identifier
- `name`: Retailer name
- `url`: Retailer website
- `country`: Retailer's country
- `industry`: Retailer's industry
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Products
Stores normalised product information.
- `id`: Unique identifier
- `identifier_value`: Product identifier (EAN, UPC, ISBN, etc.)
- `identifier_type`: Type of identifier
- `name`: Product name
- `description`: Product description
- `category`: Product category
- `attributes`: JSONB field for flexible product attributes
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Product Embeddings
Stores vector embeddings for products.
- `id`: Unique identifier
- `product_id`: Reference to products table
- `embedding_model`: Model used for embedding
- `embedding`: Vector embedding
- `created_at`: Creation timestamp

## Facet-Related Tables

### Retailer Facets
Defines facets (attributes) for each retailer.
- `id`: Unique identifier
- `retailer_id`: Reference to retailers table
- `name`: Facet name
- `description`: Facet description
- `created_at`: Creation timestamp

### Retailer Categories
Defines the category hierarchy for each retailer.
- `id`: Unique identifier
- `retailer_id`: Reference to retailers table
- `parent_id`: Reference to parent category (self-referential)
- `name`: Category name
- `description`: Category description
- `created_at`: Creation timestamp

### Retailer Category Facets
Maps facets to categories (many-to-many relationship).
- `category_id`: Reference to retailer_categories table
- `facet_id`: Reference to retailer_facets table
- `created_at`: Creation timestamp

## Product-Related Tables

### Retailer Products
Links products to retailers with retailer-specific information.
- `id`: Unique identifier
- `retailer_id`: Reference to retailers table
- `product_id`: Reference to products table
- `retailer_product_id`: Retailer's internal product ID
- `url`: Product URL
- `price`: Product price
- `availability`: Product availability
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Retailer Product Attributes
Stores retailer-specific product attributes.
- `retailer_id`: Reference to retailers table
- `retailer_product_id`: Reference to retailer_products table
- `attribute_name`: Name of the attribute
- `attribute_value`: Value of the attribute
- `attribute_type`: Type of the attribute
- `created_at`: Creation timestamp

### Attribute Mappings
Maps retailer-specific attributes to normalised attributes.
- `id`: Unique identifier
- `retailer_id`: Reference to retailers table
- `source_attribute`: Original attribute name
- `normalised_attribute`: Normalised attribute name
- `confidence`: Mapping confidence score
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Relationships

1. **Retailer → Products**
   - One-to-many through retailer_products
   - Each retailer can have multiple products

2. **Retailer → Facets**
   - One-to-many
   - Each retailer defines their own facets

3. **Retailer → Categories**
   - One-to-many
   - Each retailer has their own category hierarchy

4. **Category → Facets**
   - Many-to-many through retailer_category_facets
   - Facets can be reused across categories

5. **Product → Embeddings**
   - One-to-one
   - Each product has one embedding

## Partitioning

Some tables are partitioned by retailer_id for better performance:
- `retailer_products`
- `retailer_product_attributes`

## Indexes

Key indexes are created on:
- Foreign key columns
- Frequently queried columns
- Unique constraint columns 