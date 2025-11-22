CREATE DATABASE IF NOT EXISTS vulnerability_checker_system;
USE vulnerability_checker_system;

-- пользователи
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Тип уязвимости
CREATE TABLE vulnerability_type (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(100) UNIQUE NOT NULL -- 'sql injection','xss' и тд.
);

-- Уровень риска
CREATE TABLE risk_level (
    level_id INT AUTO_INCREMENT PRIMARY KEY,
    level_name VARCHAR(55) UNIQUE NOT NULL -- 'Critical','Low' и тд.
);

-- Уязвимости
CREATE TABLE vulnerabilities (
    vulnerability_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    risk_level_id INT,
    vulnerability_type_id INT,
    cvss_score DECIMAL(3,1),
    discovery_date DATE,
    FOREIGN KEY (risk_level_id) REFERENCES risk_level(level_id),
    FOREIGN KEY (vulnerability_type_id) REFERENCES vulnerability_type(type_id)
);

-- проекты пользователя
CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(128),
    technology_stack VARCHAR(200),
    repository_url TEXT
);

-- способ исправления
CREATE TABLE remediation_methods (
    method_id INT AUTO_INCREMENT PRIMARY KEY,
    method_name VARCHAR(255),
    description TEXT,
    code_example TEXT
);

-- связывающая таблица: найденные уязвимости
CREATE TABLE detected_vulnerabilities (
    detection_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    vulnerability_id INT,
    detection_date DATETIME NOT NULL,
    status ENUM('Open', 'In progress', 'Verified', 'Fixed'),
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(vulnerability_id)
);

-- действия по исправлению
CREATE TABLE Remediation_actions (
    action_id INT AUTO_INCREMENT PRIMARY KEY,
    detection_id BIGINT NOT NULL,
    method_id INT NOT NULL,
    assigned_to_user_id INT,
    assigned_date DATETIME,
    resolution_date DATETIME,
    FOREIGN KEY (detection_id) REFERENCES detected_vulnerabilities(detection_id),
    FOREIGN KEY (method_id) REFERENCES remediation_methods(method_id),
    FOREIGN KEY (assigned_to_user_id) REFERENCES users(user_id)
);