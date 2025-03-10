# Automated Health Check System

An asynchronous Health Check system that takes a YAML configuration file as the input for which endpoints to monitor. The interval and timeout can be set per endpoint. Writting in Python, using `uv` for package management and installation.

A small Go API has been included as well for testing purposes, which only exposes one endpoint called `/health`. This endpoint occassionaly fails, responds after 4 seconds or returns that a dependency is down.

## Installation

This project uses `uv` for dependency management. If you don't have uv installed, run the following to install on Linux/macOS:

```[bash]
curl -LsSf https://astral.sh/uv/install.sh | sh
```

or visit the [uv documentation website](https://docs.astral.sh/uv/getting-started/installation/) for more information.

For running the application using Docker & Docker compose, `docker` and `docker compose` will need to be installed as well. See the [Docker documentation website](https://docs.docker.com/engine/install/) for more information.

To be able to locally run the Go API, `go` needs to be installed. See [the Go installation page](https://go.dev/doc/install) for more information.

## Configuration

### YAML file

The application takes a YAML file as an input containing a list of endpoints. An example looks like this:

```[yaml]
endpoints:
  - name: "example"
    url: "http://test-api:8080/health"
    interval: 5s
    timeout: 3 # Optional, default is 3 seconds
```

This example can be found in the [`config/`](/config/) folder.

### Environment variables

One environment variable is needed, which contains the path of the YAML file. Another environment variable can be optionally set to increase the [amount of instances for APScheduler](https://apscheduler.readthedocs.io/en/latest/userguide.html#limiting-the-number-of-concurrently-executing-instances-of-a-job). You can create an `.env` file with the command: `touch .env` and fill this file with the following content:

```[bash]
YAML_FILE=config/example-config.yaml
MAX_INSTACES
```

This will point to the example config file in the config folder. Change accordingly to your config file.

## Running the application

### Locally

Once `uv` is installed, the project can be ran locally using the following command:

```[bash]
uv run src/main.py
```

The Go test API can be run with the following command (preferably in a different terminal):

```[bash]
cd test-api && go run main.go
```

### Docker compose

A docker compose file has been included as well. To run this application using Docker compose:

```[bash]
docker compose up -d # -d for detached mode
```

## Project structure

```
health-check/
├── config/             # Contains example and Docker configuration file
├── src/                # Contains Python code for Health Checker project
├── test-api/           # Small Go API that exposes a `/health` endpoint for testing
├── .gitignore
├── .python-version
├── docker-compose.yaml
├── Dockerfile          # Dockerfile for Python code
├── pyproject.toml      # Project metadata and dependencies
├── README.md
└── uv.lock
```

## Todo's

- [ ] Write tests
