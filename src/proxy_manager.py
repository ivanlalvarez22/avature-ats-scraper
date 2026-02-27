"""Simple proxy rotation manager."""

import threading
from pathlib import Path


class ProxyManager:
    """Manages a list of proxies with rotation and failure tracking."""
    
    def __init__(self, filepath: str = None):
        """
        Initialize proxy manager.
        
        Args:
            filepath: Path to file with one proxy per line.
                      If None, no proxies are used.
        """
        self._proxies = []
        self._bad_proxies = set()
        self._index = 0
        self._lock = threading.Lock()
        
        if filepath:
            self._load_from_file(filepath)
    
    def _load_from_file(self, filepath: str) -> None:
        """Load proxies from a text file."""
        path = Path(filepath)
        if not path.exists():
            return
        
        with open(path, "r") as f:
            for line in f:
                proxy = line.strip()
                if proxy and not proxy.startswith("#"):
                    proxy = self._normalize_proxy(proxy)
                    if proxy:
                        self._proxies.append(proxy)
    
    def _normalize_proxy(self, proxy: str) -> str | None:
        """Convert different proxy formats to standard URL format."""
        if proxy.startswith("http://") or proxy.startswith("socks"):
            return proxy
        
        parts = proxy.split(":")
        if len(parts) == 4:
            host, port, user, password = parts
            return f"http://{user}:{password}@{host}:{port}"
        elif len(parts) == 2:
            host, port = parts
            return f"http://{host}:{port}"
        
        return None
    
    def get_next(self) -> str | None:
        """
        Get the next available proxy in rotation.
        
        Returns:
            Proxy URL string or None if no proxies available.
        """
        if not self._proxies:
            return None
        
        with self._lock:
            attempts = 0
            while attempts < len(self._proxies):
                proxy = self._proxies[self._index]
                self._index = (self._index + 1) % len(self._proxies)
                
                if proxy not in self._bad_proxies:
                    return proxy
                
                attempts += 1
        
        return None
    
    def mark_bad(self, proxy: str) -> None:
        """Mark a proxy as failed."""
        with self._lock:
            self._bad_proxies.add(proxy)
    
    def mark_good(self, proxy: str) -> None:
        """Mark a proxy as working again."""
        with self._lock:
            self._bad_proxies.discard(proxy)
    
    def reset_bad(self) -> None:
        """Clear all bad proxy marks."""
        with self._lock:
            self._bad_proxies.clear()
    
    @property
    def total(self) -> int:
        """Total number of proxies loaded."""
        return len(self._proxies)
    
    @property
    def available(self) -> int:
        """Number of proxies not marked as bad."""
        return len(self._proxies) - len(self._bad_proxies)
    
    def __bool__(self) -> bool:
        """Return True if proxies are available."""
        return self.available > 0
