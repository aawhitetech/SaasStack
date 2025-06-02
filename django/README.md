# Django Backend (`django/`)

This directory contains the Django backend for the SaasStack project. It provides the REST API, user/group management, Celery task processing, and integrates with PostgreSQL and Redis.

---

## 📁 Structure

- `main_project/`  
  - Django project root (settings, wsgi, asgi, etc.)
  - `.env` – Environment variables for local/dev
  - `manage.py` – Django management script
  - `main_app/` – Main Django app:
    - `models.py` – (empty, for custom models)
    - `serializers.py` – DRF serializers for User/Group
    - `views.py` – API endpoints for users/groups (with caching and Celery integration)
    - `tasks.py` – Celery tasks (e.g., send welcome email)
    - `urls.py` – API routing
    - `admin.py`, `apps.py`, `tests.py`, `migrations/`
- `requirements.txt` – Python dependencies
- `Dockerfile` – Production-ready Docker build
- `.gitignore` – Ignore venv, cache, etc.

---

## 🚀 Getting Started

1. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2. **Configure environment:**
    - Copy or edit `main_project/.env` with your settings (see example in file).

3. **Apply migrations:**
    ```bash
    python main_project/manage.py migrate
    ```

4. **Run the development server:**
    ```bash
    python main_project/manage.py runserver
    ```

---

## 🧪 Testing

Run tests with:
```bash
python main_project/manage.py test
```

---

## ⚙️ Environment Variables

Environment variables are loaded from `main_project/.env`.

---

## 🐳 Docker

Build and run the Django API with Docker:

```bash
docker build -t saas-stack-django .
docker run --env-file main_project/.env -p 8000:8000 saas-stack-django
```

Or use the root [`docker-compose.yml`](../../docker-compose.yml) for full stack local deployment.

---

## 🔗 API Overview

- `/users/` – User CRUD (cached, triggers Celery task on create)
- `/groups/` – Group CRUD (cached)
- `/admin/` – Django admin
- `/api-auth/` – DRF login/logout

---

## 📝 License

See the root project for license information.