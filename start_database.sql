CREATE DATABASE BOT;

CREATE TABLE IF NOT EXISTS BOT.users(
    username text PRIMARY KEY,
    telegram_id int UNIQUE,
    password text,
    userrole text DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS BOT.codes(
    code text primary key
):

