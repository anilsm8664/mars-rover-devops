# Contributing

## Workflow

- `main` is always releasable. Do not commit to it directly; open a pull request.
- Work on short-lived branches named `<type>/<short-description>`, for example
  `feature/rover-cli`, `fix/smoke-test-stdin`, `ci/jenkins-pipeline`.
- Every pull request must pass the Jenkins pipeline (lint, tests, SonarQube gate, image build,
  smoke test, Trivy scan) before it is merged. Merge with a merge commit.

## Commit messages (Conventional Commits)

`<type>: <summary in the imperative>` where type is one of:
`feat`, `fix`, `test`, `build`, `ci`, `docs`, `refactor`, `chore`.

Example: `fix: stream smoke-test input through stdin`

## Before you push

Either with local Python:

```bash
ruff check rover.py tests
python -m pytest -q
```

or with Docker only:

```bash
docker compose -f docker-compose.dev.yml run --rm lint
docker compose -f docker-compose.dev.yml run --rm test
```

## Releases

Versions follow Semantic Versioning. Tag releases on `main` (`git tag -a v1.0.0 -m "..."`) and
record changes in `CHANGELOG.md`.
