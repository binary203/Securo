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
- [Лицензия](#лицензия)

## 🎯 О проекте

**SECURO** — веб-приложение для статического анализа кода на уязвимости. Использует движок [Semgrep](https://semgrep.dev) и предоставляет удобный интерфейс вместо работы напрямую с CLI. Дополнительно интегрирован ИИ-ассистент для объяснения найденных проблем.

## 🔍 Почему Semgrep?

При выборе движка анализа сравнивались несколько популярных инструментов:

| Инструмент  | Языки | Кастомные правила | Активная разработка | Точность |
|---|---|---  |---|---|
| **Bandit**  | Только Python | ❌ | Медленная | Средняя |
| **PyLint**  | Только Python | Ограничено | ✅ | Высокая (для Python) |
| **ESLint**  | JS/TS | ✅ | ✅ | Высокая (для JS) |
| **Flake8**  | Только Python | ❌ | ✅ | Средняя |
| **Semgrep** | 40+ языков | ✅ YAML | ✅ | Высокая |

**Почему Semgrep:**
- **Мультиязычность** — единый движок для 40+ языков. Bandit, ESLint, Flake8 — каждый только для своего стека
- **Паттерн-матчинг** — правила пишутся как фрагменты кода на целевом языке, а не регулярные выражения — меньше ложных срабатываний
- **Открытый реестр правил** — тысячи готовых правил от сообщества на [semgrep.dev](https://semgrep.dev/r)
- **Кастомные правила** — любая команда может написать правило под свои требования в YAML
- **Поддержка межфайлового анализа** — умеет отслеживать поток данных между функциями и файлами (dataflow)
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
| История сканирований | ❌                   | ✅ (в БД)                                 |
| Определение языка    | Вручную (`--lang`)    | Автоматически по паттернам                |

**SECURO — это самостоятельный инструмент безопасности**, который использует Semgrep как один из своих компонентов — так же как браузер использует движок рендеринга. Ключевая ценность SECURO в том, что было создано поверх:

- **ИИ-ассистент** — Semgrep только находит проблему. SECURO объясняет её, показывает вектор атаки и генерирует исправленный код
- **Преднастроенные правила** — не нужно разбираться с ruleset'ами, флагами и YAML; сканирование работает из коробки
- **Локальные паттерны определения языков** — собственная система из `LANG_PATTERNS.py` с 40+ языками работает без `--lang` флага и без интернета, создана для определения языка фрагмента кода по синтаксическим паттернам
- **Нулевой порог входа** — разработчик без опыта работы с CLI может провести полноценный аудит безопасности за 3 клика
- **Полноценная платформа** — аутентификация, история сканирований, rate limiting, красивый интерфейс — то, чего у Semgrep CLI нет по определению


## 🚀 Возможности

### Три способа ввода кода
- **Прямой ввод** — вставить код в текстовое поле
- **Загрузка файлов** — до 5 файлов, каждый до 20 МБ
- **GitHub репозиторий** — автоматическое клонирование по URL

### Анализ и результаты
- Автоматическое определение языка программирования по синтаксическим паттернам
- Карточки уязвимостей с указанием строки, фрагмента кода, типа и критичности
- Цветовая маркировка по уровням: Critical / High / Medium / Low / Info

### ИИ-ассистент
Встроен в страницу результатов. Команды:
```
/explain — объяснение уязвимости
/fix     — генерация исправленного кода
/improve — рефакторинг с учётом безопасности
```
Поддерживает русский и английский язык.

### Безопасность приложения
- CSRF-защита через Flask-WTF (`hidden_tag()`)
- Хеширование паролей через Werkzeug (PBKDF2-SHA256)
- Rate limiting: 10 запросов/мин на логин, 5/мин на регистрацию (Flask-Limiter)
- Валидация файлов: тип, размер, безопасные имена (`secure_filename`)
- Аутентификация через Flask-Login

## 🔤 Поддерживаемые языки

Python, JavaScript, TypeScript, Java, C, C++, Go, Ruby, PHP, C#, Scala, Kotlin, Rust, Swift, Lua, OCaml, Terraform, YAML, JSON, HTML, Dockerfile, Bash, Apex, Clojure, Dart, Elixir, JSX, Julia, Jsonnet, Lisp, R, Scheme, Solidity, TSX, XML, Cairo, Circom, Hack, Move

## ⚡ Быстрый старт

### Требования
- Python 3.14+
- pip
- Git (для сканирования репозиториев)
- 4 ГБ RAM (опционально, но рекомендуется)

### Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/binary203/Vulnerability_Checker.git
cd Vulnerability_Checker

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить переменные окружения
# Создать или отредактировать app/.env:
SECRET_KEY=ваш-секретный-ключ
HF_TOKEN=ваш-токен-huggingface        # для ИИ-ассистента
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
  -e HF_TOKEN="ваш-токен" \
  -e SEMGREP_APP_TOKEN="ваш-токен" \
  securo
```

## 🛠 Технический стек

### Backend
| Пакет          | Версия         | Назначение      |
|----------------|----------------|-----------------|
| Flask          | 3.1.2          | Веб-фреймворк   |
| SQLAlchemy     | 2.0.44         | ORM             |
| Flask-Login    | 0.6.3          | Аутентификация  |
| Flask-WTF      | 1.2.2          | Формы и CSRF    |
| Flask-Migrate  | 4.1.0          | Миграции БД     |
| Flask-Limiter  | 3.5+           | Rate limiting   |
| Semgrep        | latest         | SAST-движок     |
| OpenAI         | 2.9.0          | ИИ-интеграция   |
| python-dotenv  | 1.2.1          | Конфигурация    |

### Frontend
- HTML5 + Jinja2 — шаблонизация
- Vanilla CSS — терминальный тёмный дизайн
- Vanilla JS — drag-and-drop, AJAX, toast-уведомления

### База данных
- SQLite (по умолчанию)
- Поддержка PostgreSQL через `DATABASE_URL` в env

## 🏗 Архитектура

```
Vulnerability_Checker/
├── app/
│   ├── __init__.py        # Инициализация Flask + расширений
│   ├── models.py          # Модели: User, Scans, Vulnerability
│   ├── views.py           # Маршруты и контроллеры
│   ├── forms.py           # WTForms: Login, Registration, Scan
│   ├── services.py        # Semgrep-интеграция, LLM
│   ├── LANG_PATTERNS.py   # Паттерны определения языков
│   ├── .env               # Переменные окружения (не в git)
│   ├── templates/
│   │   ├── base.html      # Базовый шаблон (toast, typewriter)
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── scan.html
│   │   ├── results.html
│   │   └── 429.html       # Rate limit страница
│   └── static/
│       ├── index.css
│       ├── scan.js
│       └── ai.js
├── instance/
│   └── default.db         # SQLite БД (не в git)
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
```python
User         — id, username, password_hash, date_created
Scans        — id, user_id, date_scan, code_language, code
Vulnerability — id, scan_id, title, description, line,
                code_snippet, vulnerability_type, risk_level
```

## 👥 Разработка

### Roadmap

- [x] Статический анализ кода (Semgrep)
- [x] Три способа ввода: текст, файлы, GitHub URL
- [x] ИИ-ассистент (объяснение, исправление, улучшение)
- [x] Аутентификация пользователей
- [x] Rate limiting
- [x] Toast-уведомления
- [ ] История сканирований (модели есть, UI в разработке)
- [ ] Экспорт отчётов
- [ ] HEATMAP
- [ ] REST API

## 📄 Лицензия

[Apache License 2.0](misc/LICENSE)

---

<div align="center">

**SECURO** — Static Application Security Testing Tool

[![GitHub](https://img.shields.io/badge/GitHub-binary203%2FVulnerability_Checker-black?logo=github)](https://github.com/binary203/Vulnerability_Checker)

</div>
