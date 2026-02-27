"""HTML parser for Avature job listings."""

import re
from bs4 import BeautifulSoup
from .models import Job
from .endpoints import extract_job_id_from_url


def parse_job_listing(html: str, company: str, base_url: str) -> list[Job]:
    """
    Parse HTML page and extract job cards.
    
    Args:
        html: Raw HTML from job listing page
        company: Company name for the jobs
        base_url: Base URL of the career site
    
    Returns:
        List of Job objects
    """
    soup = BeautifulSoup(html, "lxml")
    jobs = []
    
    articles = soup.find_all("article")
    
    for article in articles:
        job = parse_job_card(article, company, base_url)
        if job:
            jobs.append(job)
    
    return jobs


def parse_job_card(article, company: str, base_url: str) -> Job | None:
    """Parse a single job card article element."""
    try:
        title_link = article.select_one("h3 a")
        if not title_link:
            return None
        
        title = title_link.get_text(strip=True)
        job_url = title_link.get("href", "")
        
        if not job_url.startswith("http"):
            job_url = base_url.rstrip("/") + job_url
        
        job_id = extract_job_id_from_url(job_url)
        if not job_id:
            return None
        
        location, date_posted = parse_job_info(article, title)
        
        description = parse_description(article)
        
        application_url = parse_apply_url(article, base_url, job_id)
        
        return Job(
            job_id=job_id,
            title=title,
            company=company,
            location=location,
            description=description,
            application_url=application_url,
            date_posted=date_posted,
            source_url=job_url,
        )
    except Exception:
        return None


def parse_job_info(article, title: str) -> tuple[str, str]:
    """Extract location and date from job info text."""
    location = "Unknown"
    date_posted = None
    
    info_divs = article.find_all("div")
    for div in info_divs:
        text = div.get_text(strip=True)
        if "Posted" in text and "Ref" in text:
            if title and text.startswith(title):
                text = text[len(title):]
            location, date_posted = extract_location_and_date(text)
            break
    
    return location, date_posted


def extract_location_and_date(text: str) -> tuple[str, str]:
    """Parse info text like 'Charlotte , NC , USA , Ref #21505 . Posted Jan-30-2026'."""
    location = "Unknown"
    date_posted = None
    
    date_match = re.search(r'Posted\s+([A-Za-z]+-\d{1,2}-\d{4})', text)
    if date_match:
        date_posted = date_match.group(1)
    
    parts = text.split(",")
    if len(parts) >= 2:
        location_parts = []
        for part in parts:
            part = part.strip()
            if "Ref" in part or "Posted" in part:
                break
            location_parts.append(part)
        if location_parts:
            location = ", ".join(location_parts)
            location = re.sub(r'\s+', ' ', location).strip()
            location = location.rstrip(" ,.")
    
    return location, date_posted


def parse_description(article) -> str:
    """Extract description preview from job card."""
    all_divs = article.find_all("div", recursive=False)
    
    for div in reversed(all_divs):
        text = div.get_text(strip=True)
        if len(text) > 50 and "Posted" not in text and "Apply" not in text:
            return clean_text(text)
    
    return ""


def parse_apply_url(article, base_url: str, job_id: str) -> str:
    """Extract or build the apply URL."""
    apply_link = article.select_one('a[href*="ApplicationMethods"]')
    if apply_link:
        url = apply_link.get("href", "")
        if not url.startswith("http"):
            return base_url.rstrip("/") + url
        return url
    
    return f"{base_url.rstrip('/')}/careers/ApplicationMethods?jobId={job_id}"


def parse_total_jobs(html: str) -> int:
    """Extract total job count from page."""
    soup = BeautifulSoup(html, "lxml")
    
    result_text = soup.find(string=re.compile(r'\d+\s*results?'))
    if result_text:
        match = re.search(r'of\s+(\d+)', result_text)
        if match:
            return int(match.group(1))
        match = re.search(r'(\d+)\s*results?', result_text)
        if match:
            return int(match.group(1))
    
    return 0


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
