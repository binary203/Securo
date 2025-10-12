CREATE DATABASE vulnerability_checker_system;
USE vulnerability_checker_system;
--пользователи
create table users (
  	user_id INT AUTO_INCREMENT primary key,
 	username varchar(255) UNIQUE NOT NULL,
  	password varchar(255) NOT NULL
  );
  --Тип уязвимости
CREATE TABLE vulnerability_type (
	type_id int AUTO_INCREMENT primary key,
  	type_name varchar(100) UNIQUE Not NULL --'sql injection','xss' и тд.
);
  --Уровень риска
CREATE table risk_level (
  level_id int AUTO_INCREMENT PRIMARY KEY,
  level_name varchar(55) UNIQUE not NULL -- 'Criticalэ','Low' и тд.
);
  --Уязвимости
CREATE TABLE vulnerabilities (
    vulnerability_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
  	risk_level_id int,
    vulnerability_type_id int,
    cvss_score DECIMAL(3,1),
    discovery_date DATE,
  	FOREIGN KEY(risk_level_id) REFERENCES risk_level(level_id),
  	FOREIGN KEY(vulnerability_type_id) REFERENCES vulnerability_type(type_id)
);
  --проекты пользователя
CREATE TABLE projects (
	project_id int AUTO_INCREMENT primary KEY,
	project_name varchar(128),
  	technology_stack varchar(200),
  	repository_url TEXT
);
  --способ исправления
CREATE TABLE remediation_methods (
	method_id int AUTO_INCREMENT primary key,
  	method_name varchar(255),
  	description text,
  	code_example text
);
  --связывающая таблица: найденные уязвимости
create TABLE detected_vulnerabilities (
	detection_id bigint AUTO_INCREMENT primary key,
  	project_id int,
  	vulnerability_id int ,
  	detection_date DATETIME NOT NULL,
  	status  ENUM('Open', 'In progress', 'Verified', 'Fixed'),
  	FOREIGN KEY(project_id) REFERENCES projects(project_id),
  	FOREIGN KEY(vulnerability_id) REFERENCES vulnerabilities(vulnerability_id)
);
--действия по исправлению
CREATE Table Remediation_actions (
	action_id INT AUTO_INCREMENT PRIMARY KEY,
  	detection_id BIGINT NOT NULL,
  	method_id INT NOT NULL,
  	assigned_to_user_id INT,
  	assigned_date DATETIME,
  	resolution_date DATETIME,
  	FOREIGN KEY(detection_id) REFERENCES detected_vulnerabilities(detection_id),
	FOREIGN KEY(method_id) REFERENCES remediation_methods(method_id),
	FOREIGN KEY(assigned_to_user_id) REFERENCES users(user_id)
);
