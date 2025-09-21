"""Tests for configuration management and host:port parsing."""

import pytest
import os
from unittest.mock import patch

from boxofports.config import parse_host_port, EjoinConfig


def test_parse_host_port_basic():
    """Test basic host:port parsing."""
    # Test host without port
    host, port = parse_host_port("192.168.1.100")
    assert host == "192.168.1.100"
    assert port == 80
    
    # Test host with default port override
    host, port = parse_host_port("192.168.1.100", default_port=8080)
    assert host == "192.168.1.100"
    assert port == 8080


def test_parse_host_port_with_port():
    """Test host:port parsing when port is included."""
    # Test host with port
    host, port = parse_host_port("203.0.113.100:60140")
    assert host == "203.0.113.100"
    assert port == 60140
    
    # Test with different port
    host, port = parse_host_port("localhost:8080")
    assert host == "localhost"
    assert port == 8080


def test_parse_host_port_edge_cases():
    """Test edge cases for host:port parsing."""
    # Test IPv6-like format (not full IPv6 support but shouldn't crash)
    host, port = parse_host_port("127.0.0.1:9090")
    assert host == "127.0.0.1"
    assert port == 9090
    
    # Test with hostname
    host, port = parse_host_port("example.com:443")
    assert host == "example.com"
    assert port == 443


def test_ejoin_config_base_url():
    """Test base URL generation with different configurations."""
    # Test normal host and port
    config = EjoinConfig(host="192.168.1.100", port=80)
    assert config.base_url == "http://192.168.1.100:80"
    
    # Test different port
    config = EjoinConfig(host="192.168.1.100", port=8080)
    assert config.base_url == "http://192.168.1.100:8080"


def test_ejoin_config_from_env_with_port():
    """Test configuration loading from environment with host:port format."""
    with patch.dict(os.environ, {
        'EJOIN_HOST': '203.0.113.100:60140',
        'EJOIN_USER': 'admin',
        'EJOIN_PASS': 'secret'
    }):
        config = EjoinConfig.from_env()
        assert config.host == "203.0.113.100"
        assert config.port == 60140
        assert config.username == "admin"
        assert config.password == "secret"
        assert config.base_url == "http://203.0.113.100:60140"


def test_ejoin_config_from_env_without_port():
    """Test configuration loading from environment without port in host."""
    with patch.dict(os.environ, {
        'EJOIN_HOST': '192.168.1.100',
        'EJOIN_PORT': '8080',
        'EJOIN_USER': 'root',
        'EJOIN_PASS': 'admin123'
    }):
        config = EjoinConfig.from_env()
        assert config.host == "192.168.1.100"
        assert config.port == 8080
        assert config.username == "root"
        assert config.password == "admin123"
        assert config.base_url == "http://192.168.1.100:8080"


def test_ejoin_config_host_port_priority():
    """Test that port in host takes priority over separate port env var."""
    with patch.dict(os.environ, {
        'EJOIN_HOST': '192.168.1.100:9090',
        'EJOIN_PORT': '8080',  # This should be ignored
        'EJOIN_USER': 'admin',
        'EJOIN_PASS': 'secret'
    }):
        config = EjoinConfig.from_env()
        assert config.host == "192.168.1.100"
        assert config.port == 9090  # Should use port from host, not EJOIN_PORT
        assert config.base_url == "http://192.168.1.100:9090"


def test_ejoin_config_missing_host():
    """Test that missing EJOIN_HOST raises appropriate error."""
    # Clear all EJOIN_ environment variables and prevent .env file loading
    env_vars_to_clear = {k: None for k in os.environ.keys() if k.startswith('EJOIN_')}
    with patch.dict(os.environ, env_vars_to_clear, clear=False):
        # Mock Path.exists to prevent .env file from being found
        with patch('boxofports.config.Path.exists', return_value=False):
            with pytest.raises(ValueError, match="EJOIN_HOST environment variable is required"):
                EjoinConfig.from_env()


def test_config_manager_basic():
    """Test basic configuration manager functionality."""
    manager = ConfigManager()
    
    # Test adding and retrieving profiles
    config = EjoinConfig(host="test.example.com", port=80)
    manager.add_profile("test", config)
    
    assert "test" in manager.list_profiles()
    retrieved = manager.get_config("test")
    assert retrieved.host == "test.example.com"
    assert retrieved.port == 80


def test_config_auth_params():
    """Test authentication parameter generation."""
    config = EjoinConfig(
        host="192.168.1.100", 
        username="testuser", 
        password="testpass"
    )
    
    auth = config.auth_params()
    assert auth == {
        "username": "testuser",
        "password": "testpass"
    }


def test_parse_host_port_invalid_port():
    """Test error handling for invalid port numbers."""
    with pytest.raises(ValueError):
        parse_host_port("192.168.1.100:invalid")
    
    with pytest.raises(ValueError):
        parse_host_port("192.168.1.100:99999999")


def test_real_world_examples():
    """Test with real-world host:port examples."""
    examples = [
        ("localhost:3000", "localhost", 3000),
        ("127.0.0.1:8080", "127.0.0.1", 8080),
        ("api.example.com:443", "api.example.com", 443),
        ("10.0.0.1:22", "10.0.0.1", 22),
        ("203.0.113.100:60140", "203.0.113.100", 60140),
        ("192.168.1.100", "192.168.1.100", 80),  # No port specified
    ]
    
    for host_spec, expected_host, expected_port in examples:
        if ":" in host_spec:
            host, port = parse_host_port(host_spec)
        else:
            host, port = parse_host_port(host_spec, 80)
        
        assert host == expected_host, f"Failed for {host_spec}"
        assert port == expected_port, f"Failed for {host_spec}"