# Test Suite for Simple APNS

This directory contains tests for the Simple APNS library. The tests use pytest and cover all aspects of the library's functionality.

## Test Structure

- `test_auth.py`: Tests for the JWT authentication token generation
- `test_payload.py`: Tests for the notification payload builder
- `test_client.py`: Tests for the APNSClient that communicates with Apple's servers
- `test_django_integration.py`: Tests for the Django integration module
- `test_exceptions.py`: Tests for the exception classes

## Running Tests

To run the tests, you need to have pytest and the required dependencies installed:

```bash
# Install dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=simple_apns

# Run specific test file
pytest tests/test_payload.py

# Run tests matching a specific name pattern
pytest -k "test_send_notification"
```

## Test Configuration

The test suite uses pytest fixtures to mock external dependencies and create test objects. The primary fixtures include:

- `mock_private_key`: A mock APNS authentication key for testing
- `mock_response_success`: A mock successful response from the APNS service
- `mock_response_error`: A mock error response from the APNS service
- `apns_test_params`: Common test parameters for creating APNSClient instances
- `mock_client`: A pre-configured APNSClient with mocked HTTP client
- `sample_payload`: A sample notification payload for testing
- `sample_device_token`: A sample device token for testing

## Running with tox

The project includes a `tox.ini` file for testing across multiple Python versions and environments:

```bash
# Install tox
pip install tox

# Run tests in all environments
tox

# Run tests in a specific environment
tox -e py39

# Run linting checks
tox -e lint

# Run type checking
tox -e mypy
```

## Writing New Tests

When adding new functionality to the library, please also add corresponding tests. Follow these guidelines:

1. Place tests in the appropriate test file based on the component being tested
2. Use pytest fixtures for setup and teardown
3. Mock external dependencies (e.g., HTTP requests, file operations)
4. Include both positive tests (expected behavior) and negative tests (error handling)
5. Aim for high code coverage (>90%)

## Code Style

Tests should follow the same code style guidelines as the main library code. Run the linting checks to ensure compliance:

```bash
tox -e lint
```