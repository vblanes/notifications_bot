CREATE TABLE IF NOT EXISTS users(
    username text PRIMARY KEY,
    telegram_id int,
    userrole text DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS codes(
    code text primary key
);

