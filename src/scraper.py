"""Avature job scraper with pagination and proxy support."""

from .http_client import HTTPClient
from .parser import parse_job_listing, parse_total_jobs
from .endpoints import build_search_url
from .models import Job
from .proxy_manager import ProxyManager


class AvatureScraper:
    """Scraper for a single Avature career site."""
    
    def __init__(
        self,
        base_url: str,
        per_page: int = 50,
        proxy_manager: ProxyManager = None
    ):
        self.base_url = base_url.rstrip("/")
        self.per_page = per_page
        self.company = self._extract_company()
        self.client = HTTPClient(proxy_manager=proxy_manager)
    
    def _extract_company(self) -> str:
        """Extract company name from subdomain."""
        host = self.base_url.split("//")[1].split("/")[0]
        subdomain = host.split(".")[0]
        return subdomain.title()
    
    def get_all_jobs(self, max_pages: int = 500) -> list[Job]:
        """Fetch all jobs from the site using pagination."""
        all_jobs = []
        offset = 0
        total_jobs = None
        page_size = None
        page_num = 1
        seen_ids = set()
        listing_endpoint = self._detect_listing_endpoint()
        if listing_endpoint != "SearchJobs":
            print(f"  Using listing endpoint: {listing_endpoint}")
        
        while page_num <= max_pages:
            url = build_search_url(
                self.base_url,
                offset=offset,
                per_page=self.per_page,
                endpoint=listing_endpoint,
            )
            
            try:
                response = self.client.get(url)
                html = response.text
            except Exception as e:
                print(f"  Error fetching page: {e}")
                break
            
            if total_jobs is None:
                total_jobs = parse_total_jobs(html)
            
            jobs = parse_job_listing(html, self.company, self.base_url)
            
            if not jobs:
                break
            
            new_jobs = [j for j in jobs if j.job_id not in seen_ids]
            if not new_jobs:
                print("(dup)", end=" ", flush=True)
                break
            
            for j in new_jobs:
                seen_ids.add(j.job_id)
            
            if page_size is None:
                page_size = len(jobs)
            
            all_jobs.extend(new_jobs)
            print(f"    p{page_num}:{len(new_jobs)}", end=" ", flush=True)
            
            offset += page_size
            page_num += 1
            
            if total_jobs and len(all_jobs) >= total_jobs:
                break
        
        return all_jobs

    def _detect_listing_endpoint(self) -> str:
        """Detect whether the site uses SearchJobs or SearchResults listings."""
        candidate_endpoints = ["SearchJobs", "SearchResults"]

        for endpoint in candidate_endpoints:
            url = build_search_url(
                self.base_url,
                offset=0,
                per_page=self.per_page,
                endpoint=endpoint,
            )

            try:
                response = self.client.get(url)
                html = response.text
            except Exception:
                continue

            if parse_job_listing(html, self.company, self.base_url):
                return endpoint

        return "SearchJobs"
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
