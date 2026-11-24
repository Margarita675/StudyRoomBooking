-- ============================================================
-- Справочный DDL схемы StudyRoomBooking (PostgreSQL).
-- Фактическая схема создаётся миграциями Django; сценарий приведён
-- для документирования структуры БД (Тема 4).
-- ============================================================

CREATE TABLE IF NOT EXISTS accounts_user (
    id              BIGSERIAL PRIMARY KEY,
    password        VARCHAR(128) NOT NULL,
    last_login      TIMESTAMPTZ,
    is_superuser    BOOLEAN NOT NULL DEFAULT FALSE,
    username        VARCHAR(150) NOT NULL UNIQUE,
    first_name      VARCHAR(150) NOT NULL,
    last_name       VARCHAR(150) NOT NULL,
    is_staff        BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined     TIMESTAMPTZ NOT NULL,
    email           VARCHAR(254) NOT NULL UNIQUE,
    role            VARCHAR(10) NOT NULL DEFAULT 'user'
                    CHECK (role IN ('user', 'admin')),
    full_name       VARCHAR(150) NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_blocked      BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS accounts_passwordresettoken (
    id          BIGSERIAL PRIMARY KEY,
    token_hash  CHAR(64) NOT NULL UNIQUE,          -- только SHA-256 хеш
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at  TIMESTAMPTZ NOT NULL,
    is_used     BOOLEAN NOT NULL DEFAULT FALSE,
    user_id     BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rooms_equipment (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS rooms_room (
    id          BIGSERIAL PRIMARY KEY,
    number      VARCHAR(20) NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    building    VARCHAR(50) NOT NULL DEFAULT '1',
    floor       SMALLINT NOT NULL DEFAULT 1 CHECK (floor >= 0),
    capacity    SMALLINT NOT NULL DEFAULT 10 CHECK (capacity > 0),
    room_type   VARCHAR(15) NOT NULL DEFAULT 'classroom'
                CHECK (room_type IN ('lecture','computer','lab','conference','classroom','universal')),
    status      VARCHAR(15) NOT NULL DEFAULT 'active'
                CHECK (status IN ('active','maintenance','closed')),
    description TEXT NOT NULL DEFAULT '',
    photo       VARCHAR(100),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rooms_roomequipment (
    id           BIGSERIAL PRIMARY KEY,
    quantity     SMALLINT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    room_id      BIGINT NOT NULL REFERENCES rooms_room(id) ON DELETE CASCADE,
    equipment_id BIGINT NOT NULL REFERENCES rooms_equipment(id) ON DELETE CASCADE,
    UNIQUE (room_id, equipment_id)
);

CREATE TABLE IF NOT EXISTS bookings_booking (
    id          BIGSERIAL PRIMARY KEY,
    date        DATE NOT NULL,
    time_start  TIME NOT NULL,
    time_end    TIME NOT NULL CHECK (time_end > time_start),
    purpose     VARCHAR(200) NOT NULL,
    comment     TEXT NOT NULL DEFAULT '',
    status      VARCHAR(12) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','confirmed','rejected','cancelled','completed')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    room_id     BIGINT NOT NULL REFERENCES rooms_room(id) ON DELETE CASCADE,
    user_id     BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS bookings_room_date_idx ON bookings_booking (room_id, date);
CREATE INDEX IF NOT EXISTS bookings_user_date_idx ON bookings_booking (user_id, date);
CREATE INDEX IF NOT EXISTS bookings_status_idx ON bookings_booking (status);
CREATE INDEX IF NOT EXISTS rooms_building_floor_idx ON rooms_room (building, floor);
CREATE INDEX IF NOT EXISTS rooms_capacity_idx ON rooms_room (capacity);
