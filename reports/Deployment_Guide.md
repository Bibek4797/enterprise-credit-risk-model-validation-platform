# Enterprise Deployment & Production Operations Guide

**Document Control & DevOps Engineering**
- **System Scope**: Production Deployment & Container Orchestration Guide
- **Target Audience**: DevOps Engineers, System Administrators, Quantitative Developers
- **Author**: Enterprise Infrastructure & DevOps Engineering Team

---

## 1. Executive Summary & Deployment Overview

This document provides deployment instructions, containerization specifications, environment configuration, and CI/CD operations for hosting the **Enterprise Credit Risk Analytics & Model Governance Platform**.

---

## 2. Containerized Deployment (Docker & Docker Compose)

The application is containerized using a multi-stage production `Dockerfile` based on `python:3.11-slim`.

### 2.1 Building & Running with Docker
```bash
# 1. Build Docker Image
docker build -t credit-risk-analytics-platform:1.0.0 .

# 2. Run Container
docker run -d -p 8501:8501 --name credit_risk_container credit-risk-analytics-platform:1.0.0
```

### 2.2 Orchestrating with Docker Compose
```bash
# Launch service in detached mode
docker-compose up -d --build
```
Access the dashboard at `http://localhost:8501`.

---

## 3. CI/CD Automated Workflow (GitHub Actions)

The repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that runs on every push and pull request to `main` or `develop`:

1. **Linting & Code Quality**: Runs `ruff check` across Python source files.
2. **Automated Testing**: Executes `pytest tests/` with code coverage tracking.
3. **Build Verification**: Validates package dependencies and import integrity.

---

## 4. Security Hardening & Environment Variables

- **Environment Configuration**: Copy `.env.example` to `.env` and configure production secrets.
- **Sensitive Data Masking**: PII masking is enforced; raw borrower identities are excluded from logs and predictions.
- **Health Checks**: Automated HTTP healthcheck endpoint configured at `http://localhost:8501/_stcore/health`.
