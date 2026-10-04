# Changelog

All notable changes are recorded here. Format based on Keep a Changelog; versions follow
Semantic Versioning.

## [Unreleased]

## [1.0.0]

### Added
- Rover CLI with input validation, error handling and logging.
- Unit tests with coverage reporting; Ruff linting.
- Non-root Docker image and container smoke test.
- Jenkins pipeline: lint, tests, SonarQube quality gate, image build, smoke test, Trivy scan,
  Artifactory publication.
- Local CI lab (Jenkins and SonarQube) and Docker-based developer tooling.
