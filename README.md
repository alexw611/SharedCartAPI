## SharedCart API
Backend API for the SharedCart Android app (IU project).

## Purpose
This API provides all server-side functionality for the SharedCart app:
user and group management, shared shopping lists, item handling,
and centralized synchronization of the application state.
The server acts as the single source of truth.
The Android app only maintains a local cache of the server state.

## Architecture
The API is implemented as a REST service using FastAPI and JWT-based
authentication (access and refresh tokens).
Data is stored in a MariaDB database and accessed via SQLAlchemy ORM.
The backend runs on a Raspberry Pi and is started automatically using systemd.
Communication is secured via HTTPS using a self-signed certificate.

## Installation
Install Python dependencies:
pip3 install -r requirements.txt

## Starting the Server
Manual start:
python3 -m uvicorn API.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=certs/key.pem --ssl-certfile=certs/cert.pem

## HTTPS
The API uses a self-signed SSL certificate for encrypted communication.
The certificate files (certs/) are not included in the repository.
To generate your own certificate:
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem -subj "/CN=sharedcart.local"
Android clients must be configured to accept self-signed certificates.

## Authentication
After login, the client receives:
an access token (short-lived, used for API requests)
a refresh token (used to automatically renew the access token)
All protected endpoints require the following HTTP header:
Authorization: Bearer <access_token>

## Snapshot
GET /snapshot
Returns all user-relevant data (groups, shopping lists, items)
in a single request.
This endpoint is used during app startup and for synchronization.

## Main Endpoints
/auth – registration, login, logout, token handling
/users/me – current user
/groups – groups and members
/lists – shopping lists
/items – shopping items
/snapshot – complete user data snapshot

## API Documentation
Interactive Swagger documentation:
https://<SERVER_IP>:8000/docs

## Operation
The API runs as a systemd service and starts automatically when the server boots.
