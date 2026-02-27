"""HTTP client with retry, rate limiting, and proxy support."""

import random
import time
from curl_cffi import requests

from .proxy_manager import ProxyManager


class HTTPClient:
    """HTTP client that impersonates a browser with optional proxy rotation."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        proxy_manager: ProxyManager = None
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.proxy_manager = proxy_manager
        self.session = requests.Session(impersonate="chrome")
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request with retry, rate limiting, and proxy rotation."""
        last_error = None
        
        for attempt in range(self.max_retries):
            proxy = self._get_proxy()
            
            try:
                self._polite_delay()
                response = self.session.get(
                    url,
                    timeout=15,
                    proxies=proxy,
                    **kwargs
                )
                response.raise_for_status()
                
                if proxy and self.proxy_manager:
                    self.proxy_manager.mark_good(proxy.get("http", ""))
                
                return response
                
            except Exception as e:
                last_error = e
                
                if proxy and self.proxy_manager:
                    self.proxy_manager.mark_bad(proxy.get("http", ""))
                
                if attempt < self.max_retries - 1:
                    wait_time = self.base_delay * (2 ** attempt)
                    time.sleep(wait_time)
        
        raise last_error
    
    def _get_proxy(self) -> dict | None:
        """Get proxy dict for requests."""
        if not self.proxy_manager:
            return None
        
        proxy_url = self.proxy_manager.get_next()
        if not proxy_url:
            return None
        
        return {"http": proxy_url, "https": proxy_url}
    
    def _polite_delay(self) -> None:
        """Random delay to be nice to servers."""
        time.sleep(random.uniform(0.3, 0.8))
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
