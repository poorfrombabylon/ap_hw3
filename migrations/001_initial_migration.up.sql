CREATE TABLE users
(
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username   VARCHAR NOT NULL UNIQUE,
    email      VARCHAR UNIQUE,
    password   VARCHAR NOT NULL,
    created_at TIMESTAMPTZ      DEFAULT NOW()
);

CREATE TABLE links
(
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    short_code    VARCHAR(10) NOT NULL UNIQUE,
    custom_alias  VARCHAR(50) UNIQUE,
    original_url  TEXT        NOT NULL,
    user_id       UUID REFERENCES users (id),
    created_at    TIMESTAMPTZ      DEFAULT NOW(),
    click_count   INTEGER          DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    expires_at    TIMESTAMPTZ
);