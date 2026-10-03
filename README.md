# Mars Rover DevOps Coding Exercise

Production-style Python CLI implementation of the Mars Rover exercise, delivered through Jenkins CI.

## What is included

- Python CLI with validation, error handling and logging
- Unit tests and coverage
- Ruff linting
- Docker containerization with non-root runtime
- Container smoke test
- Trivy HIGH/CRITICAL vulnerability gate
- SonarQube analysis and enforced quality gate
- Jenkins pipeline as code
- Secure Jenkins credentials for Artifactory
- Artifactory Docker image publication
- Example valid and invalid inputs
- Documentation and reproducible commands

## Prerequisites

Local: Python 3.12+, pip and Docker.

Jenkins agent: Python 3.12+, Docker, Trivy and SonarQube Scanner. Jenkins must have Pipeline support and a SonarQube installation named `sonarqube`.

## Local execution

```bash
python rover.py examples/input.txt
```

Expected stdout:

```text
1 3 N
5 1 E
```

Logs are written to stderr so stdout remains suitable for automation.

## Input format

The first line is the upper-right plateau coordinate; lower-left is `0 0`. Each rover has a position line followed by a command line.

Valid directions: `N E S W`.

Valid commands: `L R M`.

Official example:

```text
5 5
1 2 N
LMLMLMLMM
3 3 E
MMRMMRMRRM
```

## Error behavior

Invalid plateau coordinates, rover positions, directions, commands, empty commands, incomplete rover pairs, unreadable files and moves outside the plateau cause a non-zero exit code. A move outside the plateau is rejected before changing rover state.

## Tests

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pytest -q
pytest -q --cov=rover --cov-report=term-missing --cov-report=xml:coverage.xml
```

## Lint

```bash
ruff check rover.py tests
```

## Docker

```bash
docker build --pull -t mars-rover:local .
docker run --rm -v "$PWD/examples/input.txt:/input.txt:ro" mars-rover:local /input.txt
```

The image runs as UID 10001 rather than root.

## Jenkins pipeline

The complete CI definition is in `Jenkinsfile` and contains these mandatory stages:

1. Checkout and setup
2. Code validation/lint
3. Unit tests
4. SonarQube analysis
5. SonarQube quality gate
6. Docker build
7. Container smoke test
8. Trivy vulnerability gate
9. Artifactory publication

The pipeline is configured to fail on lint/test/quality-gate/smoke/security failures. Artifactory publication is restricted to `main`.

### Jenkins prerequisites

Configure:

- SonarQube installation name: `sonarqube`
- SonarQube webhook to Jenkins so `waitForQualityGate` can return
- SonarQube Scanner available to the agent
- Docker and Trivy on the agent
- Username/password credential ID: `artifactory-docker`
- Job/environment variables: `ARTIFACTORY_REGISTRY` and `ARTIFACTORY_REPOSITORY`

Never commit Artifactory credentials or tokens to Git. Jenkins injects them only during the publish step and Docker receives the password through `--password-stdin`.

## SonarQube

`sonar-project.properties` defines the project metadata and coverage report. The Jenkinsfile runs analysis and then uses `waitForQualityGate abortPipeline: true`, so a failed mandatory quality gate stops the pipeline.

## Security

- No runtime third-party dependencies
- Development dependencies are explicitly declared
- Secrets stay in Jenkins Credentials
- Docker runs as a non-root user
- Smoke-test input is mounted read-only
- Trivy scans the final image
- Docker build uses `--pull`
- No credentials are logged or committed

## Artifactory

The image is tagged using the Jenkins build number:

```text
<registry>/<repository>/mars-rover:<BUILD_NUMBER>
```

Actual registry/repository values are environment-specific and must be provided by the organization.

If Artifactory access is unavailable for the exercise, keep the publish stage configured with these environment variables and document that publication requires the supplied registry and Jenkins credential. The rest of the pipeline must still execute successfully.

## Design decisions

The rover domain logic is isolated in a small `Rover` class. Parsing and validation are separate functions so the business logic can be tested independently. Proposed movement is validated before state is changed. The CLI uses stdout for final results and stderr for operational/error logs.

The application uses only the Python standard library at runtime, minimizing supply-chain exposure.

## Known limitations

This is a CLI exercise, not a network service. SonarQube and Artifactory require organization infrastructure/credentials. Jenkins agents require the listed build tools.

## Suggested Git history

Use small, meaningful commits such as:

```text
Initial Mars Rover application
Add validation and error handling
Add unit tests and coverage
Add linting
Add Docker containerization
Add Jenkins CI pipeline
Add SonarQube quality gate
Add smoke and security checks
Add Artifactory publication
Improve documentation
```
