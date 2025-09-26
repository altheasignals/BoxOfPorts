"""Pytest configuration and shared fixtures."""

import asyncio
import tempfile
from pathlib import Path

import pytest


# Configure asyncio event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_config_file(temp_dir):
    """Create a temporary config file for testing."""
    config_content = """
[gateway1]
host = 192.168.1.100
username = admin
password = admin123

[gateway2]
host = 192.168.1.101:9090
username = user
password = secret456

[settings]
timeout = 30
max_retries = 3
    """.strip()

    config_file = temp_dir / "test_config.ini"
    config_file.write_text(config_content)

    return config_file


# Pytest configuration
pytest_plugins = []

# Add custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test that requires real gateway connection"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )


# Skip integration tests by default unless explicitly requested
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle integration tests."""
    if config.getoption("--integration"):
        # Don't skip integration tests if explicitly requested
        return

    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests that require real gateway connections"
    )
