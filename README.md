
# CloudX Store

A containerized e-commerce application built using Flask, PostgreSQL, HTML, CSS, and JavaScript.

The project demonstrates a simple three-tier application architecture with Docker Compose.

## Architecture

```text
User Browser
    |
    v
Frontend - Nginx
    |
    v
Backend - Flask + Gunicorn
    |
    v
Database - PostgreSQL
```

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Web Server | Nginx |
| Backend | Python, Flask |
| Application Server | Gunicorn |
| Database | PostgreSQL 16 |
| Containerization | Docker |
| Orchestration | Docker Compose |
| Version Control | Git, GitHub |

## Project Structure

```text
cloudx-store/
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── nginx.conf
│   └── Dockerfile
│
├── backend/
│   ├── app.py
│   ├── db.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Application Features

- User registration and login
- Session-based authentication
- Product listing
- Shopping cart
- Order placement
- Order history
- PostgreSQL data persistence
- Frontend and backend communication through REST APIs

## Prerequisites

Install the following:

- Docker
- Docker Compose
- Git

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/deepakpatra-tech/cloudx-store.git

cd cloudx-store
```

### 2. Configure environment variables

Create your local environment file:

```bash
cp .env.example .env
```

Update `.env` with your own values:

```env
DB_NAME=cloudx_store
DB_USER=cloudx_user
DB_PASSWORD=your_secure_password
SECRET_KEY=your_random_secret_key
```

Never commit your actual `.env` file to GitHub.

### 3. Build and start containers

```bash
docker compose up -d --build
```

### 4. Check container status

```bash
docker compose ps
```

### 5. Access the application

Open your browser:

http://localhost:8080

## Docker Services

| Service | Description |
|---|---|
| frontend | Nginx serves the frontend and proxies API requests |
| backend | Flask application running with Gunicorn |
| db | PostgreSQL database |

## Useful Docker Commands

Start application:

```bash
docker compose up -d
```

Rebuild application:

```bash
docker compose up -d --build
```

View running containers:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f
```

Stop application:

```bash
docker compose down
```

Stop and delete database volume:

```bash
docker compose down -v
```

Warning: The last command permanently removes the project's PostgreSQL volume and its stored data.

## Data Persistence

PostgreSQL uses a Docker named volume to retain database data when containers are stopped or recreated.

## Learning Objectives

This project is designed as a hands-on DevOps learning project covering:

- Docker image creation
- Docker Compose orchestration
- Multi-container application architecture
- Database persistence
- Environment variable management
- Git and GitHub
- CI/CD automation (planned)
- Infrastructure as Code (planned)
- Monitoring and observability (planned)

## Author

Deepak Patra

GitHub: https://github.com/deepakpatra-tech
