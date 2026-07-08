-- v2: passphrase generation mode on orders (run once on existing DB)
ALTER TABLE orders ADD COLUMN IF NOT EXISTS generation_mode VARCHAR(20) NOT NULL DEFAULT 'random';
