-- v3: email breach watch subscriptions
CREATE TABLE IF NOT EXISTS watch_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    known_breach_names JSONB NOT NULL DEFAULT '[]'::jsonb,
    expires_at TIMESTAMPTZ NOT NULL,
    last_checked_at TIMESTAMPTZ,
    last_notified_at TIMESTAMPTZ,
    last_order_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_watch_subscriptions_email ON watch_subscriptions (email);
CREATE INDEX IF NOT EXISTS ix_watch_subscriptions_status ON watch_subscriptions (status);
CREATE INDEX IF NOT EXISTS ix_watch_subscriptions_expires_at ON watch_subscriptions (expires_at);
