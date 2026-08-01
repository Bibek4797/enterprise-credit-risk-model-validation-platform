# Production Deployment & Infrastructure Guide

**Document Control & DevOps Infrastructure Manual**
- **System Scope**: Containerization, Orchestration, CI/CD & Production Hardening
- **Target Audience**: DevOps Engineers, System Administrators, Infrastructure Quants
- **Author**: Enterprise Infrastructure & DevOps Engineering Team

---

## 1. Multi-Stage Docker Containerization

The repository includes a multi-stage `Dockerfile` based on `python:3.11-slim` exposing port `8501`.

### Docker Commands
```bash
# Build Docker Image
docker build -t credit-risk-analytics-platform:1.0.0 .

# Run Container
docker run -d -p 8501:8501 --name credit_risk_container credit-risk-analytics-platform:1.0.0
```

### Docker Compose
```bash
docker-compose up -d --build
```

---

## 2. GitHub Actions CI/CD Pipeline

The `.github/workflows/ci.yml` workflow automates linting (`ruff check`), type checking (`mypy`), and test suite execution (`pytest tests/`) on every push to `main` or `develop`.
