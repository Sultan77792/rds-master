-- Создание таблицы пользователей
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role_id INT NOT NULL,
    region VARCHAR(100),
    kgu_oopt VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Создание таблицы пожаров
CREATE TABLE fires (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date_reported DATETIME NOT NULL,
    region VARCHAR(100) NOT NULL,
    kgu_oopt VARCHAR(100) NOT NULL,
    branch VARCHAR(100),
    forestry VARCHAR(100),
    quarter VARCHAR(50),
    vydel VARCHAR(50),
    area_total FLOAT NOT NULL,
    area_forest FLOAT,
    area_covered FLOAT,
    area_top FLOAT,
    area_non_forest FLOAT,
    forest_guard_involved BOOLEAN DEFAULT FALSE,
    forest_guard_people INT DEFAULT 0,
    forest_guard_vehicles INT DEFAULT 0,
    aps_involved BOOLEAN DEFAULT FALSE,
    aps_people INT DEFAULT 0,
    aps_vehicles INT DEFAULT 0,
    aps_aircraft INT DEFAULT 0,
    emergency_involved BOOLEAN DEFAULT FALSE,
    emergency_people INT DEFAULT 0,
    emergency_vehicles INT DEFAULT 0,
    emergency_aircraft INT DEFAULT 0,
    local_involved BOOLEAN DEFAULT FALSE,
    local_people INT DEFAULT 0,
    local_vehicles INT DEFAULT 0,
    local_aircraft INT DEFAULT 0,
    other_involved BOOLEAN DEFAULT FALSE,
    other_people INT DEFAULT 0,
    other_vehicles INT DEFAULT 0,
    other_aircraft INT DEFAULT 0,
    description TEXT,
    damage DECIMAL(15,2),
    suppression_cost DECIMAL(15,2),
    kpo VARCHAR(100),
    attachment VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id INT,
    FOREIGN KEY (created_by_id) REFERENCES users(id)
);

-- Создание таблицы аудита
CREATE TABLE audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT,
    changes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);