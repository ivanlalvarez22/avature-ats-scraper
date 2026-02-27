"""
Avature API endpoints and URL patterns.

Discovered by analyzing: ally.avature.net, broadinstitute.avature.net, astellas.avature.net
"""


# Base URL patterns
# Some sites have locale prefix: /{locale}/careers (e.g., /en_US/, /en_GB/)
# Some sites don't: /careers
BASE_PATTERNS = [
    "https://{subdomain}.avature.net/careers",
    "https://{subdomain}.avature.net/{locale}/careers",
]


# Job listing endpoint (HTML, not JSON)
# Returns paginated list of jobs rendered in HTML
SEARCH_JOBS = "/SearchJobs/"
SEARCH_RESULTS = "/SearchResults/"

# Pagination parameters
# jobRecordsPerPage: jobs per page (default 6 or 10)
# jobOffset: skip N jobs (0, 6, 12, 18... or 0, 10, 20, 30...)
PAGINATION_PARAMS = {
    "records_per_page": "jobRecordsPerPage",
    "offset": "jobOffset",
}


# Job detail patterns
# Pattern 1: /careers/JobDetail/{slug}/{id}
# Pattern 2: /careers/JobDetail?jobId={id}
JOB_DETAIL_PATTERNS = [
    "/careers/JobDetail/{slug}/{job_id}",
    "/careers/JobDetail?jobId={job_id}",
]


# Apply to job
APPLICATION_URL = "/careers/ApplicationMethods?jobId={job_id}"


# HTML selectors for parsing job listings
SELECTORS = {
    "job_card": "article",
    "job_title": "h3 a",
    "job_link": "h3 a",
    "job_info": "article > div",
    "pagination_info": '[class*="result"]',
    "next_page": 'a[href*="jobOffset"]',
}


# Example URLs discovered:
#
# ally.avature.net:
#   - List: /careers/SearchJobs/?jobRecordsPerPage=6&jobOffset=6
#   - Detail: /careers/JobDetail/Senior-Front-End-Site-Reliability-Engineer/15738
#   - Total: 66 jobs
#
# broadinstitute.avature.net:
#   - List: /en_US/careers/SearchJobs/?jobRecordsPerPage=6&jobOffset=6
#   - Detail: /en_US/careers/JobDetail/Research-Scientist-I/21285
#   - Total: 37 jobs
#
# astellas.avature.net:
#   - List: /en_GB/careers/SearchJobs/?jobOffset=10
#   - Detail: /en_GB/careers/JobDetail/Statistical-Science-Lead/5710
#   - Total: 133 jobs


def build_search_url(
    base_url: str,
    offset: int = 0,
    per_page: int = 50,
    endpoint: str = "SearchJobs",
) -> str:
    """Build URL to fetch job listings."""
    base = base_url.rstrip("/")
    endpoint_clean = endpoint.strip("/")
    return f"{base}/{endpoint_clean}/?jobRecordsPerPage={per_page}&jobOffset={offset}"


def build_job_url(base_url: str, job_id: str, slug: str = "") -> str:
    """Build URL for job detail page."""
    base = base_url.rstrip("/")
    if slug:
        return f"{base}/JobDetail/{slug}/{job_id}"
    return f"{base}/JobDetail?jobId={job_id}"


def extract_job_id_from_url(url: str) -> str:
    """Extract job ID from a job detail URL."""
    if "jobId=" in url:
        return url.split("jobId=")[1].split("&")[0]
    
    parts = url.rstrip("/").split("/")
    for part in reversed(parts):
        if part.isdigit():
            return part
    
    return ""
