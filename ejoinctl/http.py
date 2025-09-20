"""HTTP client factory with authentication, retries, and proper error handling."""

import asyncio
import logging
from typing import Any, Optional

import httpx
from httpx import Response

from .config import EjoinConfig

logger = logging.getLogger(__name__)


class EjoinHTTPError(Exception):
    """Base exception for EJOIN HTTP API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class EjoinAuthError(EjoinHTTPError):
    """Authentication error for EJOIN API."""
    pass


class EjoinTimeoutError(EjoinHTTPError):
    """Timeout error for EJOIN API."""
    pass


class EjoinClient:
    """HTTP client for EJOIN Multi-WAN Router API with retry logic."""
    
    def __init__(self, config: EjoinConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "EjoinClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_client(self) -> None:
        """Ensure the HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=httpx.Timeout(
                    connect=self.config.connect_timeout,
                    read=self.config.read_timeout,
                    write=self.config.connect_timeout,
                    pool=self.config.connect_timeout,
                ),
                headers={
                    "User-Agent": "ejoinctl/0.1.0",
                    "Accept": "application/json",
                },
            )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
        retry_count: int = 0,
    ) -> Response:
        """Make an HTTP request with retry logic."""
        await self._ensure_client()
        
        # Merge auth params with provided params
        final_params = {**self.config.auth_params()}
        if params:
            final_params.update(params)
        
        # Set appropriate content type for JSON requests
        final_headers = {}
        if json:
            final_headers["Content-Type"] = "application/json;charset=utf-8"
        if headers:
            final_headers.update(headers)
        
        try:
            # Log request (but mask password)
            masked_params = final_params.copy()
            if "password" in masked_params:
                masked_params["password"] = "***"
            logger.debug(f"{method} {url} params={masked_params}")
            
            response = await self._client.request(
                method=method,
                url=url,
                params=final_params,
                json=json,
                data=data,
                headers=final_headers or None,
            )
            
            # Check for authentication errors
            if response.status_code == 401:
                raise EjoinAuthError(
                    "Authentication failed. Check username and password.",
                    status_code=response.status_code
                )
            
            # Check for other HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = f"HTTP {response.status_code}: {error_data.get('reason', 'Unknown error')}"
                except Exception:
                    message = f"HTTP {response.status_code}: {response.text}"
                
                raise EjoinHTTPError(
                    message,
                    status_code=response.status_code,
                    response=error_data if 'error_data' in locals() else None
                )
            
            return response
            
        except httpx.TimeoutException as e:
            if retry_count < self.config.max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                logger.warning(f"Request timeout, retrying in {wait_time}s (attempt {retry_count + 1}/{self.config.max_retries})")
                await asyncio.sleep(wait_time)
                return await self._make_request(method, url, params, json, data, headers, retry_count + 1)
            
            raise EjoinTimeoutError(f"Request timed out after {self.config.max_retries} retries") from e
            
        except httpx.ConnectError as e:
            if retry_count < self.config.max_retries:
                wait_time = 2 ** retry_count
                logger.warning(f"Connection error, retrying in {wait_time}s (attempt {retry_count + 1}/{self.config.max_retries})")
                await asyncio.sleep(wait_time)
                return await self._make_request(method, url, params, json, data, headers, retry_count + 1)
            
            raise EjoinHTTPError(f"Connection failed after {self.config.max_retries} retries: {e}") from e
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500 and retry_count < self.config.max_retries:
                wait_time = 2 ** retry_count
                logger.warning(f"Server error {e.response.status_code}, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
                return await self._make_request(method, url, params, json, data, headers, retry_count + 1)
            
            raise EjoinHTTPError(
                f"HTTP {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code
            ) from e
    
    async def get(self, url: str, params: Optional[dict] = None, **kwargs) -> Response:
        """Make a GET request."""
        return await self._make_request("GET", url, params=params, **kwargs)
    
    async def post(self, url: str, json: Optional[dict] = None, data: Optional[dict] = None, params: Optional[dict] = None, **kwargs) -> Response:
        """Make a POST request."""
        return await self._make_request("POST", url, params=params, json=json, data=data, **kwargs)
    
    async def get_json(self, url: str, params: Optional[dict] = None, **kwargs) -> dict[str, Any]:
        """Make a GET request and return JSON response."""
        response = await self.get(url, params=params, **kwargs)
        return response.json()
    
    async def post_json(self, url: str, json: Optional[dict] = None, data: Optional[dict] = None, params: Optional[dict] = None, **kwargs) -> dict[str, Any]:
        """Make a POST request and return JSON response."""
        response = await self.post(url, json=json, data=data, params=params, **kwargs)
        return response.json()


def create_client(config: EjoinConfig) -> EjoinClient:
    """Create an EJOIN HTTP client with the given configuration."""
    return EjoinClient(config)


# Synchronous wrapper for backward compatibility
class SyncEjoinClient:
    """Synchronous wrapper for EjoinClient."""
    
    def __init__(self, config: EjoinConfig):
        self.config = config
        self._client = EjoinClient(config)
    
    def _run_async(self, coro):
        """Run an async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # We're in an async context, create a new loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    
    def get_json(self, url: str, params: Optional[dict] = None, **kwargs) -> dict[str, Any]:
        """Make a GET request and return JSON response."""
        async def _get():
            async with self._client:
                return await self._client.get_json(url, params=params, **kwargs)
        return self._run_async(_get())
    
    def post_json(self, url: str, json: Optional[dict] = None, data: Optional[dict] = None, params: Optional[dict] = None, **kwargs) -> dict[str, Any]:
        """Make a POST request and return JSON response."""
        async def _post():
            async with self._client:
                return await self._client.post_json(url, json=json, data=data, params=params, **kwargs)
        return self._run_async(_post())


    def get_sms_inbox(self, sms_id: int = 1, sms_num: int = 0, delete_after: bool = False) -> dict[str, Any]:
        """Query SMS inbox from the device.
        
        Args:
            sms_id: Starting SMS ID (1-based)
            sms_num: Number of SMS to query (0 = all)
            delete_after: Delete SMS after query (0 = no, 1 = yes)
            
        Returns:
            SMS inbox response with messages
        """
        params = {
            "sms_id": sms_id,
            "sms_num": sms_num,
            "sms_del": 1 if delete_after else 0,
        }
        
        return self.get_json("/goip_get_sms.html", params=params)


def create_sync_client(config: EjoinConfig) -> SyncEjoinClient:
    """Create a synchronous EJOIN HTTP client."""
    return SyncEjoinClient(config)
