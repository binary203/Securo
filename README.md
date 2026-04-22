# SECURO — Статический Анализатор Кода на Уязвимости

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green)
![Semgrep](https://img.shields.io/badge/Semgrep-latest-orange)
![License](https://img.shields.io/badge/License-Apache%202.0-red)

> **Your Code is Safe!** — Статический анализ кода на уязвимости с веб-интерфейсом и ИИ-ассистентом.

## 📋 Оглавление

- [О проекте](#о-проекте)
- [Почему Semgrep?](#почему-semgrep)
- [SECURO vs Semgrep CLI](#securo-vs-semgrep-cli)
- [Возможности](#возможности)
- [Поддерживаемые языки](#поддерживаемые-языки)
- [Быстрый старт](#быстрый-старт)
- [Технический стек](#технический-стек)
- [Архитектура](#архитектура)
- [Персональные данные и 152-ФЗ](#персональные-данные-и-152-фз)
- [Лицензия](#лицензия)

## 🎯 О проекте

**SECURO** — веб-приложение для статического анализа кода на уязвимости. Использует движок [Semgrep](https://semgrep.dev) и предоставляет удобный интерфейс вместо работы напрямую с CLI. Дополнительно интегрирован ИИ-ассистент на базе Google Gemini для объяснения найденных проблем.

## 🔍 Почему Semgrep?

При выборе движка анализа сравнивались несколько популярных инструментов:

| Инструмент  | Языки | Кастомные правила | Активная разработка | Точность |
|---|---|---|---|---|
| **Bandit**  | Только Python | ❌ | Медленная | Средняя |
| **PyLint**  | Только Python | Ограничено | ✅ | Высокая (для Python) |
| **ESLint**  | JS/TS | ✅ | ✅ | Высокая (для JS) |
| **Flake8**  | Только Python | ❌ | ✅ | Средняя |
| **Semgrep** | 40+ языков | ✅ YAML | ✅ | Высокая |

**Почему Semgrep:**
- **Мультиязычность** — единый движок для 40+ языков
- **Паттерн-матчинг** — правила пишутся как фрагменты кода, а не регулярные выражения — меньше ложных срабатываний
- **OWASP Top 10** — встроенный набор правил покрывает все 10 категорий критических уязвимостей
- **Открытый реестр** — тысячи готовых правил от сообщества на [semgrep.dev](https://semgrep.dev/r)
- **CI/CD-ready** — официальная интеграция с GitHub Actions, GitLab CI, Jenkins

## ⚖️ SECURO vs Semgrep CLI

Semgrep — это CLI-инструмент для разработчиков. SECURO делает его доступным для всех:

| Параметр             | Semgrep CLI          | SECURO                                     |
|----------------------|----------------------|--------------------------------------------|
| Интерфейс            | Командная строка     | Веб-браузер                                |
| Установка            | Требуется Python,pip | Только браузер                             |
| Ввод кода            | Файлы на диске       | Текст / файлы / GitHub URL                 |
| Результаты           | JSON / SARIF / текст | Визуальные карточки с цветовой маркировкой |
| Объяснение           | ❌                   | ✅ ИИ-ассистент                           |
| Исправление кода     | ❌                   | ✅ `/fix` команда                         |
| Аутентификация       | ❌                   | ✅ Регистрация и профиль                  |
| История сканирований | ❌                   | ✅ Полная история с экспортом             |
| Определение языка    | Вручную (`--lang`)   | Автоматически по паттернам                |

## 🚀 Возможности

### Три способа ввода кода
- **Прямой ввод** — вставить код в текстовое поле
- **Загрузка файлов** — до 5 файлов, каждый до 20 МБ
- **GitHub / GitLab репозиторий** — автоматическое клонирование по URL

### Анализ и результаты
- Автоматическое определение языка по синтаксическим паттернам (`LANG_PATTERNS.py`)
- Карточки уязвимостей: строка, фрагмент кода, тип и уровень критичности
- Фильтрация по уровню: Высокий / Средний / Низкий
- Цветовая маркировка: Critical/High → 🔴, Medium/Warning → 🟠, Low/Info → 🟡

### ИИ-ассистент (Google Gemini)
Встроен в страницу результатов. Команды:
```
/explain — объяснение уязвимости на языке пользователя
/fix     — генерация исправленного кода
/improve — рефакторинг с учётом безопасности
```
Поддерживает русский и английский язык.

### История и экспорт
- Все сканирования сохраняются в профиле пользователя
- Таблица истории с датой, языком, количеством уязвимостей по уровням
- Просмотр любого прошлого сканирования
- Экспорт результатов в JSON

### Безопасность приложения
- CSRF-защита на всех POST-формах (Flask-WTF `hidden_tag()`)
- Хеширование паролей: Werkzeug PBKDF2-SHA256
- Cookie: `HttpOnly`, `SameSite=Lax`, `Secure` в production
- Security Headers: CSP, X-Frame-Options, X-Content-Type-Options, HSTS
- Rate limiting: 10 req/min на логин, 5 req/min на регистрацию, 20 req/hour на сканирование
- Валидация файлов: тип, размер (max 20 МБ), безопасные имена (`secure_filename`)
- Лимит загрузки: 110 МБ на один запрос (Flask `MAX_CONTENT_LENGTH`)

## 🔤 Поддерживаемые языки

Python, JavaScript, TypeScript, Java, C, C++, Go, Ruby, PHP, C#, Scala, Kotlin, Rust, Swift, Lua, OCaml, Terraform, YAML, JSON, HTML, Dockerfile, Bash, Apex, Clojure, Dart, Elixir, JSX, Julia, Jsonnet, Lisp, R, Scheme, Solidity, TSX, XML, Cairo, Circom, Hack, Move

## ⚡ Быстрый старт

### Требования
- Python 3.11+
- pip
- Git (для сканирования репозиториев)

### Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/binary203/Vulnerability_Checker.git
cd Vulnerability_Checker

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить переменные окружения
# Создать файл app/.env:
SECRET_KEY=ваш-секретный-ключ
GEMINI_API_KEY=ваш-ключ-google-gemini
SEMGREP_APP_TOKEN=ваш-токен-semgrep   # опционально

# 4. Запустить
python start.py
```

Откройте `http://localhost:5000`

### Запуск через Docker

```bash
docker build -t securo .
docker run -p 5000:5000 \
  -e SECRET_KEY="ваш-секретный-ключ" \
  -e GEMINI_API_KEY="ваш-ключ" \
  -e SEMGREP_APP_TOKEN="ваш-токен" \
  securo
```

## 🛠 Технический стек

### Backend
| Пакет               | Версия  | Назначение               |
|---------------------|---------|--------------------------|
| Flask               | 3.1.2   | Веб-фреймворк            |
| SQLAlchemy          | 2.0+    | ORM                      |
| Flask-Login         | 0.6.3   | Аутентификация сессий    |
| Flask-WTF           | 1.2.2   | Формы и CSRF-защита      |
| Flask-Migrate       | 4.1.0   | Миграции БД              |
| Flask-Limiter       | 3.5+    | Rate limiting            |
| Semgrep             | latest  | SAST-движок              |
| google-generativeai | latest  | ИИ-ассистент (Gemini)    |
| Werkzeug            | 3.1+    | Хеширование паролей      |
| python-dotenv       | 1.2.1   | Конфигурация окружения   |

### Frontend
- HTML5 + Jinja2 — шаблонизация
- Vanilla CSS — терминальный тёмный дизайн
- Vanilla JS — drag-and-drop, fetch API, toast-уведомления

### База данных
- SQLite (по умолчанию, development)
- PostgreSQL через переменную `DATABASE_URL` (production)

## 🏗 Архитектура

```
Vulnerability_Checker/
├── app/
│   ├── __init__.py        # Инициализация Flask, расширений, security headers
│   ├── models.py          # Модели: User, Scans, Vulnerability
│   ├── views.py           # Маршруты и контроллеры
│   ├── forms.py           # WTForms: Login, Registration, Scan, Logout
│   ├── services.py        # Semgrep-интеграция, LLM (Gemini)
│   ├── LANG_PATTERNS.py   # Паттерны определения языков (40+)
│   ├── .env               # Переменные окружения (не в git)
│   ├── templates/
│   │   ├── base.html      # Базовый шаблон (navbar, toast, typewriter)
│   │   ├── index.html     # Лендинг с фичами и шагами
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html   # Профиль со статистикой по severity
│   │   ├── scan.html      # Форма сканирования с loader'ом
│   │   ├── results.html   # Результаты с фильтром и ИИ-ассистентом
│   │   ├── history.html   # История сканирований с пагинацией
│   │   └── 429.html       # Страница rate limit
│   └── static/
│       ├── index.css
│       ├── scan.js
│       └── ai.js
├── config.py              # DevelopmentConfig / ProductionConfig
├── start.py               # Точка входа + init_db()
├── requirements.txt
└── Dockerfile
```

### Паттерн MVC

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   View      │────▶│  Controller  │────▶│   Model     │
│ (Templates) │     │  (views.py)  │     │ (models.py) │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Services    │
                    │ (services.py)│
                    └──────────────┘
```

### Модели БД
```
User          — id, username, password_hash, date_created
Scans         — id, user_id, date_scan, code_language, code
Vulnerability — id, scan_id, title, description, line,
                code_snippet, vulnerability_type, risk_level
```

## 🔐 Персональные данные и 152-ФЗ

В соответствии с Федеральным законом № 152-ФЗ «О персональных данных»:

**Что хранит SECURO:**
- `username` — псевдоним, выбранный пользователем (не ФИО, не e-mail)
- `password_hash` — хеш пароля (PBKDF2-SHA256), оригинал пароля не хранится
- `date_created` — дата регистрации
- Код, загружаемый для сканирования — хранится привязанным к аккаунту

**Меры защиты:**
- Пароли никогда не хранятся в открытом виде
- Доступ к данным только у авторизованного владельца аккаунта
- Передача данных по HTTPS в production-режиме (HSTS)
- Cookie-сессии защищены флагами `HttpOnly` и `SameSite`

**Минимизация данных (ст. 5, п. 1.5 152-ФЗ):**  
Регистрация требует только придуманный логин и пароль — никакие реальные персональные данные (ФИО, телефон, e-mail) не запрашиваются и не хранятся.

## 👥 Roadmap

- [x] Статический анализ кода (Semgrep + OWASP Top 10)
- [x] Три способа ввода: текст, файлы, GitHub/GitLab URL
- [x] ИИ-ассистент — объяснение, исправление, улучшение кода
- [x] Аутентификация пользователей
- [x] Rate limiting и security headers
- [x] История сканирований
- [x] Экспорт результатов в JSON
- [x] Фильтрация уязвимостей по уровню критичности
- [ ] HEATMAP уязвимостей
- [ ] REST API

## 📄 Лицензия

[Apache License 2.0](misc/LICENSE)

---

<div align="center">

**SECURO** — Static Application Security Testing Tool

[![GitHub](https://img.shields.io/badge/GitHub-binary203%2FVulnerability_Checker-black?logo=github)](https://github.com/binary203/Vulnerability_Checker)

</div>
