# SaasStack

A modern, production-ready SaaS application stack built with:

* **Django**: REST API backend
* **Celery**: Task queue for async jobs
* **Redis**: Caching and Celery broker/result backend
* **PostgreSQL**: Relational database
* **Next.js**: Frontend web application
* **Docker Compose**: Local development orchestration
* **AWS CDK (Python)**: Infrastructure-as-code for ECS Fargate deployment

---

## 🧱 Architecture Overview

```
Frontend (Next.js)
   |
   ↓
API Gateway / ALB
   |
   ↓
Django REST API ←→ PostgreSQL
       ↑
       ↓
   Redis (Cache & Celery)
       ↑
    Celery Workers
```

---

## 🧪 Local Development

### Prerequisites

* Docker & Docker Compose
* Python 3.11+
* Node.js 18+

### Quick Start

```bash
# Clone the repo
git clone https://github.com/aawhitetech/SaasStack.git
cd SaasStack

# Start the local stack
docker compose up --build
```

Services available:

* Frontend: [http://localhost:3000](http://localhost:3000)
* Django API: [http://localhost:8000/](http://localhost:8000/)
* Redis: localhost:6379
* Postgres: localhost:5432

---

## 🚀 AWS Deployment

Infrastructure is defined with **AWS CDK (Python)** for:

* ECS Fargate cluster (API, Celery, Redis, Web)
* RDS PostgreSQL instance (with Secrets Manager)
* Application Load Balancer for frontend
* Secure security group mappings
* Private subnets with NAT Gateway

### Deploy

```bash
cd cdk
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cdk bootstrap
cdk deploy
```

---

## 📂 Project Structure

```
SaasStack/
├── django/             # Django project (API + Celery)
├── web_app/            # Next.js frontend
├── aws_cdk/            # AWS CDK infrastructure code
├── docker-compose.yml  # Local dev orchestration
└── README.md
```

---

## 🛠️ Future Improvements

* Add HTTPS support with ACM / cert-manager
* CI/CD pipeline with GitHub Actions
* Autoscaling
* Liveness / Readiness Probes

---

## 🧑‍💻 Author

Developed by [Aaron White](https://github.com/aawhitetech)

---
