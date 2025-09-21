"""Tests for HTTP client functionality."""

import pytest
from unittest.mock import AsyncMock, patch
import httpx

from boxofports.http import APIClient
from boxofports.config import GatewayConfig
from boxofports.models import (
    SMSTask,
    SendSMSRequest,
    SendSMSResponse,
    DeviceStatusRequest,
    DeviceStatusResponse,
    APIError,
)


@pytest.fixture
def gateway_config():
    """Test gateway configuration."""
    return GatewayConfig(
        host="192.168.1.1",
        username="admin",
        password="admin123"
    )


@pytest.fixture
def api_client(gateway_config):
    """Test API client instance."""
    return APIClient(gateway_config)


@pytest.mark.asyncio
async def test_client_initialization(gateway_config):
    """Test client initialization."""
    client = APIClient(gateway_config)
    assert client.config == gateway_config
    assert client.base_url == "http://192.168.1.1:8080/cgi-bin/sms"
    
    # Test with custom port
    config_with_port = GatewayConfig(
        host="192.168.1.1:9090",
        username="admin",
        password="admin123"
    )
    client = APIClient(config_with_port)
    assert client.base_url == "http://192.168.1.1:9090/cgi-bin/sms"


@pytest.mark.asyncio
async def test_send_sms_success(api_client):
    """Test successful SMS sending."""
    mock_response = httpx.Response(
        200,
        json={"status": 0, "msg": "OK"},
        request=httpx.Request("POST", "http://test.com")
    )
    
    with patch.object(api_client.session, 'post', return_value=mock_response) as mock_post:
        sms_task = SMSTask(
            ports=["1A"],
            message="Test message",
            phone_numbers=["1234567890"]
        )
        
        response = await api_client.send_sms(sms_task)
        
        assert response.status == 0
        assert response.msg == "OK"
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "/sendsms"
        
        # Check request data
        data = call_args[1]["data"]
        assert data["username"] == "admin"
        assert data["password"] == "admin123"
        assert data["action"] == "sendsms"
        assert data["port"] == "1A"
        assert data["text"] == "Test message"
        assert data["number"] == "1234567890"


@pytest.mark.asyncio
async def test_send_sms_api_error(api_client):
    """Test SMS sending with API error."""
    mock_response = httpx.Response(
        200,
        json={"status": 1, "msg": "Invalid port"},
        request=httpx.Request("POST", "http://test.com")
    )
    
    with patch.object(api_client.session, 'post', return_value=mock_response):
        sms_task = SMSTask(
            ports=["1A"],
            message="Test message",
            phone_numbers=["1234567890"]
        )
        
        with pytest.raises(APIError) as exc_info:
            await api_client.send_sms(sms_task)
        
        assert exc_info.value.status_code == 1
        assert exc_info.value.message == "Invalid port"


@pytest.mark.asyncio
async def test_send_sms_http_error(api_client):
    """Test SMS sending with HTTP error."""
    with patch.object(api_client.session, 'post', side_effect=httpx.HTTPError("Connection failed")):
        sms_task = SMSTask(
            ports=["1A"],
            message="Test message",
            phone_numbers=["1234567890"]
        )
        
        with pytest.raises(APIError) as exc_info:
            await api_client.send_sms(sms_task)
        
        assert "HTTP error" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_device_status_success(api_client):
    """Test successful device status retrieval."""
    mock_response = httpx.Response(
        200,
        json={
            "status": 0,
            "msg": "OK",
            "data": {
                "device_id": "TEST001",
                "signal_strength": 20,
                "network_status": "connected",
                "ports": [
                    {"port": "1A", "status": "ready", "imei": "123456789012345"},
                    {"port": "1B", "status": "locked", "imei": "123456789012346"}
                ]
            }
        },
        request=httpx.Request("POST", "http://test.com")
    )
    
    with patch.object(api_client.session, 'post', return_value=mock_response):
        request = DeviceStatusRequest()
        response = await api_client.get_device_status(request)
        
        assert response.status == 0
        assert response.msg == "OK"
        assert response.data.device_id == "TEST001"
        assert response.data.signal_strength == 20
        assert len(response.data.ports) == 2


@pytest.mark.asyncio
async def test_test_connection_success(api_client):
    """Test successful connection test."""
    mock_response = httpx.Response(
        200,
        json={"status": 0, "msg": "OK"},
        request=httpx.Request("POST", "http://test.com")
    )
    
    with patch.object(api_client.session, 'post', return_value=mock_response):
        result = await api_client.test_connection()
        assert result is True


@pytest.mark.asyncio
async def test_test_connection_failure(api_client):
    """Test connection test failure."""
    with patch.object(api_client.session, 'post', side_effect=httpx.HTTPError("Connection failed")):
        result = await api_client.test_connection()
        assert result is False


@pytest.mark.asyncio
async def test_context_manager(gateway_config):
    """Test client as context manager."""
    async with APIClient(gateway_config) as client:
        assert client.session is not None
    
    # Session should be closed after exiting context
    # We can't directly test this without accessing private attributes


@pytest.mark.asyncio
async def test_client_retry_logic(api_client):
    """Test client retry logic on failures."""
    # Mock first call to fail, second to succeed
    responses = [
        httpx.HTTPError("Connection failed"),
        httpx.Response(
            200,
            json={"status": 0, "msg": "OK"},
            request=httpx.Request("POST", "http://test.com")
        )
    ]
    
    with patch.object(api_client.session, 'post', side_effect=responses):
        result = await api_client.test_connection()
        # The retry logic is handled by httpx-retry, so this should succeed
        # after the first failure
        assert result is True


def test_format_auth_data(api_client):
    """Test authentication data formatting."""
    auth_data = api_client._format_auth_data({"action": "test"})
    
    expected = {
        "username": "admin",
        "password": "admin123",
        "action": "test"
    }
    
    assert auth_data == expected