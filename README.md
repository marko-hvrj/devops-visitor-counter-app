# DevOps Visitor Counter App

This simple HTTP application uses Redis to track and store the number of visits to a web page. The application serves as a practical demonstration of DevOps concepts and tools used for app development, containterization, health checks, automated testing and countinous integration with GitHub Actions.

Technologies:
-Python 3.12 / Flask
-Redis 7.4
-Docker
-Docker Compose
-Bash / curl
-pytest / Ruff
-Git / GitHub Actions

Architecture:
                 Browser / curl
                       |
                       | HTTP :8080
                       v
             +-------------------+
             | Flask application |
             |   Docker service  |
             |       app         |
             +-------------------+
                       |
                       | Redis protocol :6379
                       | (internal Docker network)
                       v
             +-------------------+
             |       Redis       |
             |   Docker service  |
             |       redis       |
             +-------------------+
                       |
                       v
             +-------------------+
             | Named Docker      |
             | volume: redis_data|
             +-------------------+

Only the Flask application's HTTP port is published to the host. Redis is accessible over the internal Compose network to the application and is not exposed to the host. Redis stores it's data in a named Docker volume.

Prerequisites:
-Docker Desktop, or Docker Engine with the Compose plugin, installed and running.
-Git, to clone the repository
-An availavle local TCP port 8080

Python and Redis do not need to be installed separately when using Docker Compose.

==================== Quick Start =======================

1.Clone the repository
Bash
git clone https://github.com/marko-hvrj/devops-visitor-counter-app.git
cd devops-visitor-counter-app

2.Create the local enviroment file from the supplied template
-macOS/Linux
Bash
cp .env.example .env 
-Windows
powershell
Copy-Item .env.example .env

Keep APP_PORT = 8080 for documented default setup.

3.Build and start both services
Bash
docker compose up -d --build

Compose builds the Flask image, starts Redis, waits for Redis to become healthy, and starts the application. 

4.Verify the application

Open the URLs in a browser, or use curl:

Bash
curl http://localhost:8080/
curl http://localhost:8080/visits
curl http://localhost:8080/health

The hostname and visit count will vary. Each request to /visits increases the counter, requests to / do not.

5.Stop the application
Bash
docker compose down

This removes the Compose containers and network but preserves the named Redis volume. To start again run 
docker compose up -d
Avoid 
docker compose down -v
if you want to retain the counter, because -v removes named volumes.

The Compose file sets REDIS_HOST=redis, allowing Docker's internal DNS to resolve the Redis service by name. For a locally running Flask process outside Docker, REDIS_HOST=127.0.0.1 can be used if a Redis server is reachable on the host.

================= Bash health check ====================

The script accepts an endpoint URL, makes up to five attempts, waits three seconds between unsuccessful attempts, and prints the timestamp and HTTP status for each attempt. It exits with code 0 on HTTP 200 and 1 if no attempt succeeds or the URL argument is missing.

bash scripts/healthcheck.sh http://localhost:8080/health

================= Testing and Continous Integration ====================

The repository includes a pytest test for the root endpoint. To run the existing test locally with a Python environment containing the dependencies:

python -m pip install -r requirements.txt
REDIS_HOST=127.0.0.1 REDIS_PORT=6379 python -m pytest -v

The current root-endpoint test does not need an active Redis connection, but the environment variables must be set because the Redis client is configured when app.py is imported. The test suite currently verifies the root endpoint; it does not yet provide automated integration coverage for /visits and /health.

Run the linter with:

python -m pip install ruff
python -m ruff check .

The GitHub Actions workflow is defined in .github/workflows/ci.yml. 
It runs on:
-Pushes to main
-Pull requests targeting main

The CI job checks out the repository, configures Python 3.12, installs dependencies, runs Ruff, executes pytest, and builds the Docker image. A failed step causes the job to fail. The badge at the top links to the workflow's status and run history.

=================== Technical Decisions ==========================

Small, pinned base image. 
The Dockerfile uses python:3.12-slim rather than a larger general-purpose Python image. This reduces the image's size while keeping a standard Python runtime.

Docker build caching. 
requirements.txt is copied and installed before app.py. Docker can reuse the dependency-installation layer when only application code changes, speeding up subsequent builds.

Non-root application user. 
The application runs as appuser rather than root, reducing privileges inside the container.

Named volume and Redis persistence. 
Redis stores its data under /data using the redis_data volume. Append-only persistence (--appendonly yes) helps retain the counter across container recreation. A regular docker compose down does not delete the named volume.

Internal service networking. 
Only the Flask HTTP port is published. Redis remains on the internal Compose network, reducing unnecessary exposure. The app connects using the service name redis instead of a hard-coded IP address.

Startup readiness and restart behavior. 
The Redis container has a health check, and the application waits for Redis to report healthy before starting. Both services use restart: unless-stopped to recover from unexpected exits.

Simple CI pipeline. 
Ruff catches code-quality issues, pytest checks existing application behavior, and the Docker build validates that the application image can be produced. Pull-request checks help detect problems before changes are merged into main.

===================== Problems encountered and solutions =============================

Python dependency and command availability. 
Running pip directly was not always possible in the local shell. Activating the project's .venv and using python -m pip ensured packages were installed in the intended Python environment.

Ruff import-order warnings. 
Ruff reported I001 warnings for unsorted imports in app.py and spacing around imports in test_app.py. Running python -m ruff check . --fix organized the imports, and a subsequent lint check passed.

====================== Future Impovements ===============================

-Add integration tests for /visits and both successful and failing /health responses, using a Redis service in CI or test doubles where appropriate.

-Multi-stage Docker build: Optimize the Docker image by separating build-time dependencies from the runtime environment, and compare image sizes before and after optimization.

-GitHub Container Registry (GHCR): Extend the CI pipeline to automatically publish Docker images to GHCR on pushes to main, tagged with the corresponding commit SHA.

-Nginx reverse proxy and load balancing: Introduce Nginx as a reverse proxy and run two application instances to demonstrate load balancing, using the host field in API responses to identify individual instances.

-Kubernetes deployment: Create Deployment, Service, and ConfigMap manifests and deploy the application to a local Kubernetes cluster using kind or minikube.

-Security scanning: Integrate Trivy into the CI pipeline to detect known vulnerabilities in Docker images.

-Makefile automation: Introduce a Makefile with make build, make up, make test, and make down commands to simplify common development tasks.

-Extended automated testing: Add integration tests for the Redis visitor counter and health endpoint, including scenarios where Redis is unavailable.