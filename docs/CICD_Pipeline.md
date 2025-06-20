# CI/CD Pipeline Documentation

## 1. Overview

This document outlines the Continuous Integration/Continuous Deployment (CI/CD) pipeline for the Wildfire CLI project. The pipeline automates testing, quality checks, and deployment to staging and production environments on DigitalOcean App Platform. Its goal is to ensure code quality, stability, and efficient delivery of new features.

## 2. Workflows

All CI/CD workflows are defined in `.github/workflows/`.

### a. Run Tests and Coverage (`run_tests_and_coverage.yml`)

*   **Purpose**: Executes automated tests and generates code coverage reports.
*   **Triggers**:
    *   On push to the `main` branch.
    *   On pull requests targeting the `main` branch.
*   **Key Steps**:
    1.  Checks out code.
    2.  Sets up Python environment.
    3.  Installs dependencies from `requirements.txt`.
    4.  Runs `pytest` from the `tests/` directory.
    5.  Generates a code coverage report (`coverage.xml` and terminal summary) for the `src/` directory.
    6.  Uploads `coverage.xml` as an artifact named `coverage-report`.

### b. Code Quality Gate (`code_quality_gate.yml`)

*   **Purpose**: Enforces coding standards, security checks, and code coverage requirements on pull requests.
*   **Triggers**: On pull requests targeting `main` (specifically changes to `src/**`, `tests/**`, `*.py`).
*   **Key Checks**:
    1.  **Test Execution & Coverage**: Runs `pytest` and checks if code coverage meets the defined threshold (currently >20%). Fails if below threshold.
    2.  **Code Formatting (Black)**: Ensures code formatting consistency.
    3.  **Style Guide Compliance (Flake8)**: Checks for PEP 8 and other style violations.
    4.  **Type Checking (MyPy)**: Performs static type checking. (Note: Currently uses `--ignore-missing-imports`; consider making stricter in the future).
    5.  **Security Scanning (Bandit)**: Identifies common security vulnerabilities in Python code.
    6.  **Reporting**: Posts a summary comment on the pull request with the results of all checks.

### c. Deploy to Staging (`deploy_staging.yml`)

*   **Purpose**: Automatically deploys the application to a staging environment on DigitalOcean App Platform.
*   **Triggers**: On push to the `main` branch.
*   **Key Steps**:
    1.  Checks out code from the `main` branch.
    2.  Installs `doctl` (DigitalOcean CLI).
    3.  Authenticates `doctl` using the `DIGITALOCEAN_ACCESS_TOKEN` secret.
    4.  Deploys the application using the `.do/app-staging.yaml` specification to the DigitalOcean app specified by `STAGING_APP_ID`.
*   **Required Secrets**:
    *   `DIGITALOCEAN_ACCESS_TOKEN`: For `doctl` authentication.
    *   `STAGING_APP_ID`: The ID of the DigitalOcean app designated for staging.

### d. Deploy to Production (`deploy_production.yml`)

*   **Purpose**: Manually deploys the application to the production environment on DigitalOcean App Platform, including smoke testing and automated rollback.
*   **Triggers**: Manually via `workflow_dispatch` from the GitHub Actions UI. Can optionally specify a commit SHA to deploy.
*   **Key Steps**:
    1.  Checks out the specified commit (or `main` branch HEAD).
    2.  Installs and authenticates `doctl`.
    3.  Deploys the application using the `.do/app.yaml` (production) specification to the DigitalOcean app specified by `PRODUCTION_APP_ID`.
    4.  **Smoke Tests**: Executes a placeholder smoke test script. **This needs to be implemented with actual application health checks.**
    5.  **Automated Rollback**: If smoke tests fail, the workflow attempts to roll back to the previously active successful deployment.
*   **Required Secrets**:
    *   `DIGITALOCEAN_ACCESS_TOKEN`.
    *   `PRODUCTION_APP_ID`: The ID of the DigitalOcean app designated for production.

## 3. Testing

*   **Test Location**: Unit and integration tests are located in the `tests/` directory.
*   **Running Tests Locally**:
    ```bash
    pip install -r requirements.txt  # Ensure pytest and pytest-cov are installed
    pytest tests/
    ```
*   **Coverage**:
    *   To run tests with coverage locally:
        ```bash
        pytest --cov=src tests/
        ```
    *   The current coverage threshold enforced in pull requests is **>20%**. This should be gradually increased towards the goal of **>90%**.

## 4. Deployment

### Staging Environment
*   Deployment to staging is **automated** and occurs on every push/merge to the `main` branch.
*   The staging app specification is defined in `.do/app-staging.yaml`.

### Production Environment
*   Deployment to production is **manual**.
*   To trigger a production deployment:
    1.  Navigate to the "Actions" tab in the GitHub repository.
    2.  Under "Workflows", select "🚀 Deploy to Production (Manual)".
    3.  Click "Run workflow". You can optionally specify a commit SHA.
*   The production app specification is defined in `.do/app.yaml`.
*   **Important**: Ensure smoke tests in `deploy_production.yml` are robust before relying heavily on automated rollback.

## 5. Required Secrets

The following secrets must be configured in the GitHub repository settings (Settings > Secrets and variables > Actions) for the CI/CD pipeline to function correctly:

*   `DIGITALOCEAN_ACCESS_TOKEN`: Your DigitalOcean API token with read and write access.
*   `STAGING_APP_ID`: The ID of your DigitalOcean App Platform application used for the staging environment.
*   `PRODUCTION_APP_ID`: The ID of your DigitalOcean App Platform application used for the production environment.

## 6. Next Steps / Future Enhancements

This CI/CD pipeline provides a solid foundation. Future enhancements can include:

*   **Comprehensive Smoke Tests**: Implement thorough smoke tests for the production deployment workflow.
*   **Performance Testing**: Integrate automated performance testing (e.g., using k6, Locust) into the pipeline, possibly run against the staging environment.
*   **Advanced Deployment Strategies**:
    *   **Canary Releases**: Gradually roll out changes to a subset of users in production.
    *   **Feature Flags**: Implement feature flags for controlled feature rollout and A/B testing.
*   **Infrastructure as Code (IaC)**: Manage DigitalOcean resources using tools like Terraform.
*   **Enhanced Monitoring and Alerting**: Integrate more detailed monitoring (e.g., Prometheus, Grafana) and set up alerts for key application metrics and deployment statuses beyond DigitalOcean defaults.
*   **Secrets Management**: Implement a more robust secrets management solution (e.g., HashiCorp Vault, Doppler) if complexity grows.
*   **Code Coverage Enforcement**: Gradually increase the required code coverage threshold in `code_quality_gate.yml` towards >90%.
*   **Environment Promotion**: Consider a more formal promotion process (e.g., staging build becomes a release candidate for production).
*   **Security Scanning**: Integrate more advanced security scanning tools (SAST, DAST) if needed.
*   **Deployment Documentation**: Expand runbooks and troubleshooting guides for deployments.

```
