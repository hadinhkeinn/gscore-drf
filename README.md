# GSCore (Django REST API)

A lightweight Django 5 + DRF project that stores THPT 2024 student scores and exposes
REST endpoints for:

* CRUD operations on student scores
* Aggregate **score-level reports** (Excellent / Good / …)
* Ranking **Top students** in *Group A* (Math + Physics + Chemistry)

---

## 1  Quick start

```bash
# 1. Clone & enter the project directory
$ git clone <repo-url> gscore_be_drf && cd gscore_be_drf

# 2. Create and activate a virtual-env (Python ≥ 3.11)
$ python -m venv venv
$ source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Copy the sample environment file and adjust values
$ cp .env.example .env
$ nano .env                  # or your favourite editor

# 5. Run database migrations
$ python manage.py migrate

# 6. (Optional) Import the provided CSV of scores
$ python manage.py import_scores path/to/diem_thi_thpt_2024.csv

# 7. Fire up the development server
$ python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/v1/…`.

---

## 2  Environment variables (`.env`)

Key | Description | Default in `.env.example`
----|-------------|---------------------------
`SECRET_KEY` | Django secret key | — *(generate your own)*
`DEBUG` | Debug mode (`True`/`False`) | `False`
`ALLOWED_HOSTS` | Comma-separated list of hosts | `*`
`DB_ENGINE` | Django DB engine | `django.db.backends.mysql`
`DB_NAME` | Database name | `myapp_db`
`DB_USER` | Database user | `your_db_user`
`DB_PASSWORD` | Database password | `your_db_password`
`DB_HOST` | DB host | `localhost`
`DB_PORT` | DB port | `3306`

> When running **locally** you may simply set `DEBUG=True` and leave
> `ALLOWED_HOSTS=*`.

---

## 3  Database

This project uses **MySQL** by default.  You may switch to PostgreSQL or SQLite by
modifying `DB_ENGINE` (and installing the relevant driver) – Django takes care of
schema migrations.

---

## 4  Management commands

Command | Purpose
--------|---------
`python manage.py import_scores <csv> [--truncate] [--dry-run]` | Bulk-import student scores from the official CSV.

Run `python manage.py help import_scores` for all flags.

---

## 5  API reference (v1)

Method | Endpoint | Description
-------|----------|------------
GET | `/api/v1/scores/` | List student scores (paginated)
POST | `/api/v1/scores/` | Create a score record
GET | `/api/v1/scores/<sbd>/` | Retrieve by ID (`r_number`)
PUT/PATCH | `/api/v1/scores/<sbd>/` | Update
DELETE | `/api/v1/scores/<sbd>/` | Delete
GET | `/api/v1/score-report/` | Score-level statistics for all subjects
GET | `/api/v1/score-report/chart-data/` | Chart-ready dataset
GET | `/api/v1/score-report/subject/<subject>/` | Detailed stats for one subject
GET | `/api/v1/top-students/group-a/` | Top students in Group A

> All endpoints return JSON and follow the format `{ "success": bool, "data": … }`.

---

## 6  Running tests

_No tests yet – contributions welcome!_

---

## 7  Deployment hints

1. Ensure `DEBUG=False` and a strong `SECRET_KEY`.
2. Serve static files with **WhiteNoise** (already installed) or your web server.
3. Behind a reverse proxy (nginx / Apache) point `/` to `gunicorn myapp.wsgi`.
4. Put the management command inside a cron or Celery beat if you need regular imports.

---
