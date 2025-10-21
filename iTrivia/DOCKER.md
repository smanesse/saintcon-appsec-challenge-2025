# Docker Setup for iTrivia

Single Docker container that builds the Rust/Dioxus frontend and runs the Common Lisp backend server.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Build and start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Application: http://localhost:6006

## Available Commands

- `docker-compose up --build` - Build and start the application
- `docker-compose up -d` - Start in detached mode
- `docker-compose down` - Stop the application
- `docker-compose logs` - View logs

## Architecture

### Single Container Build
- **Frontend:** Rust + Dioxus with cargo-chef for optimal caching
- **Backend:** Common Lisp (SBCL) using official Docker image
- **Database:** SQLite with persistent volume
- **Serving:** Lisp backend serves both API and static frontend files

## Database

The SQLite database (`itrivia.db`) is mounted as a volume, so data persists between container restarts.

## Development

For development with live reload:
```bash
make dev
```

This will build and start all services with live logging.

## Troubleshooting

1. **Port conflicts:** Make sure ports 3000 and 6006 are not in use
2. **Build issues:** Try `make clean` then `make build`
3. **Database issues:** Check that the database file has proper permissions

## File Structure

```
.
├── docker-compose.yml          # Main orchestration file
├── Dockerfile.backend         # Backend (Lisp) Dockerfile
├── itrivia-app/
│   ├── Dockerfile             # Frontend (Rust) Dockerfile
│   └── nginx.conf             # Nginx configuration
├── .dockerignore              # Docker ignore files
└── Makefile                   # Convenience commands
```
