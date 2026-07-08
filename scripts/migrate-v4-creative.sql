-- Creative product: store category and seed words per order
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS order_options JSONB NOT NULL DEFAULT '{}'::jsonb;
