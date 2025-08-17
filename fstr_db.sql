-- Создаем таблицу пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    fam VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    otc VARCHAR(255),
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создаем таблицу координат
CREATE TABLE coords (
    id SERIAL PRIMARY KEY,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    height INTEGER NOT NULL
);

-- Создаем таблицу перевалов
CREATE TABLE pereval_added (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    coord_id INTEGER NOT NULL REFERENCES coords(id),
    beauty_title VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    other_titles VARCHAR(255),
    connect TEXT,
    add_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    winter_level VARCHAR(10),
    summer_level VARCHAR(10),
    autumn_level VARCHAR(10),
    spring_level VARCHAR(10),
    status VARCHAR(10) DEFAULT 'new' CHECK (status IN ('new', 'pending', 'accepted', 'rejected'))
);

-- Создаем таблицу изображений
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    data BYTEA
);

-- Создаем таблицу связи перевалов и изображений
CREATE TABLE pereval_images (
    pereval_id INTEGER NOT NULL REFERENCES pereval_added(id),
    image_id INTEGER NOT NULL REFERENCES images(id),
    PRIMARY KEY (pereval_id, image_id)
);