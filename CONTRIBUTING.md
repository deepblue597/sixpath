 ---                                                                                              
  # Contributing to SixPath                                                                        
                                                                                                   
  Thank you for your interest in contributing! This document explains how to get started.

  ## Project Structure

  sixpath/
  ├── apps/
  │   ├── backend/        # FastAPI backend
  │   └── frontend/       # Streamlit frontend (legacy)
  ├── packages/
  │   └── models/         # Shared Pydantic models
  ├── docker-compose.yml
  └── .env.example

  ## Prerequisites

  - [Docker](https://docs.docker.com/get-docker/) & Docker Compose
  - [uv](https://docs.astral.sh/uv/) (Python package manager)
  - Python 3.13+

  ## Local Development Setup

  1. Clone the repository:
     ```bash
     git clone https://github.com/your-username/sixpath.git
     cd sixpath

  2. Create your .env file:
  cp .env.example .env
  # Fill in the required values, generate JWT secret with:
  openssl rand -hex 64
  3. Start all services:
  docker compose up --build
  4. For backend development without Docker:
  cd apps/backend
  uv sync
  uv run uvicorn api:app --reload

  How to Contribute

  Reporting Bugs

  Open an issue with:
  - A clear title and description
  - Steps to reproduce
  - Expected vs actual behavior
  - Your OS, Docker version, and any relevant logs

  Suggesting Features

  Open an issue with the enhancement label. Describe the use case and why it fits SixPath's goal of
   private, self-hosted network management.

  Submitting a Pull Request

  1. Fork the repository and create a branch from master:
  git checkout -b feat/your-feature-name
  2. Make your changes. Keep commits focused and descriptive.
  3. Test your changes with Docker Compose before submitting.
  4. Open a PR against master with:
    - A clear description of what changed and why
    - Screenshots if the change affects the UI

  Code Style

  - Backend: Follow standard Python conventions (PEP 8). Use type hints.
  - Models: Shared Pydantic models live in packages/models/ — changes there affect both apps.
  - API: New endpoints go in apps/backend/routers/, with corresponding DAO and service layers.

  Areas Open for Contribution

  - Frontend improvements (the React frontend is actively replacing the Streamlit one)
  - New graph layout options
  - Import/export of contacts (CSV, vCard)
  - Better mobile support
  - Test coverage (unit & integration tests)
  - Documentation

  License

  By contributing, you agree that your contributions will be licensed under the project's [Apache License Version 2.0](https://github.com/deepblue597/sixpath?tab=Apache-2.0-1-ov-file#readme).

