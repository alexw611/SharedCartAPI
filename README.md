<p align="center">
  <h1 align="center">🛒 SharedCart API</h1>
  <p align="center">
    <strong>RESTful backend service for collaborative shopping list management</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
    <img src="https://img.shields.io/badge/MariaDB-003545?style=for-the-badge&logo=mariadb&logoColor=white" alt="MariaDB">
    <img src="https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT">
  </p>
</p>

---

## About

SharedCart API is the backend service powering a collaborative Android shopping app. It enables users to create groups, manage shared shopping lists in real time, and keep all devices in sync. The server acts as the **single source of truth** — the mobile client maintains only a local cache.

## Features

- **User Management** — Registration, login, and profile handling
- **Group System** — Create and manage shopping groups with multiple members
- **Shared Lists & Items** — Collaborative shopping lists with real-time item management
- **Snapshot Sync** — Single-endpoint data synchronization for efficient client updates
- **JWT Authentication** — Secure access & refresh token flow
- **HTTPS** — Encrypted communication via TLS/SSL

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) |
| Database | [MariaDB](https://mariadb.org/) |
| Auth | JWT (Access + Refresh Tokens) |
| Server | Uvicorn (ASGI) |
| Hosting | Raspberry Pi + systemd |
| Transport | HTTPS (self-signed certificate) |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive token pair |
| `POST` | `/auth/refresh` | Refresh the access token |
| `POST` | `/auth/logout` | Invalidate the current session |
| `GET` | `/users/me` | Get current user profile |
| `GET` | `/groups` | List all groups for the user |
| `POST` | `/groups` | Create a new group |
| `GET` | `/lists` | Get shopping lists |
| `POST` | `/lists` | Create a new shopping list |
| `GET` | `/items` | Get items in a list |
| `POST` | `/items` | Add an item |
| `PUT` | `/items/{id}` | Update an item |
| `DELETE` | `/items/{id}` | Remove an item |
| `GET` | `/snapshot` | Full data snapshot for sync |

> 📖 **Interactive API docs** available at `https://<SERVER_IP>:8000/docs` (Swagger UI)

## Authentication Flow

```
Client                          Server
  │                               │
  ├── POST /auth/login ──────────►│
  │                               ├── Validate credentials
  │◄── { access_token,           │
  │      refresh_token } ─────────┤
  │                               │
  ├── GET /snapshot ─────────────►│
  │   Authorization: Bearer <at>  │
  │◄── { user data } ────────────┤
  │                               │
  ├── POST /auth/refresh ────────►│
  │   { refresh_token }           │
  │◄── { new access_token } ─────┤
```

All protected endpoints require the header:
```
Authorization: Bearer <access_token>
```

## Getting Started

### Prerequisites

- Python 3.11+
- MariaDB instance
- OpenSSL (for certificate generation)

### Installation

```bash
# Clone the repository
git clone https://github.com/alexw611/SharedCartAPI.git
cd SharedCartAPI

# Install dependencies
pip3 install -r requirements.txt
```

### Generate SSL Certificate

```bash
mkdir -p certs
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -subj "/CN=sharedcart.local"
```

### Run the Server

```bash
python3 -m uvicorn API.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --ssl-keyfile=certs/key.pem \
  --ssl-certfile=certs/cert.pem
```

The API runs as a **systemd service** in production and starts automatically on boot.

## Project Structure

```
SharedCartAPI/
├── API/
│   ├── main.py            # FastAPI app & route registration
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── auth.py            # JWT token logic
│   ├── database.py        # DB connection & session
│   └── routers/           # Endpoint modules
│       ├── auth.py
│       ├── users.py
│       ├── groups.py
│       ├── lists.py
│       └── items.py
├── requirements.txt
└── README.md
```

> ⚠️ *The actual file structure may vary slightly. Certificate files (`certs/`) and environment configs are not included in the repository.*

## License

This project was developed as part of a university course (IU).

---

