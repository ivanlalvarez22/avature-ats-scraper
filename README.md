# Avature ATS Scraper

A scraper to get job posts from Avature websites.

## How to Install

```bash
pip install -r requirements.txt
```

## How to Use

```bash
python main.py
```

## Project Structure

```text
avature-ats-scraper/
├── input/              # Input files (URLs, sites)
├── output/             # Jobs and stats
├── scripts/            # Helper scripts
├── src/                # Main code
├── main.py             # Start here
├── requirements.txt    # Dependencies
└── README.md           # This file
```

## Data Preprocessing

The starter pack includes a very large URL list (`Urls.txt`). Many entries are duplicates or outdated job links.

Instead of scraping all URLs directly, this project does:

1. Extract unique `*.avature.net` subdomains from `Urls.txt`
2. Build normalized career roots (`https://<subdomain>.avature.net/careers`)
3. Optionally enrich with Certificate Transparency (`crt.sh`) in validation step
4. Validate active sites
5. Scrape each validated site with pagination

Why this is better:

| Naive way | Smart way |
|---|---|
| Massive URL-by-URL crawl | Crawl validated company career roots |
| Many 404 and stale links | Current listings from active sites |
| Duplicate-heavy output | Global dedup by `job_id` |

## Reverse Engineering

I analyzed multiple Avature tenants and implemented robust patterns used across sites.

Key finding: Avature listings are rendered in HTML (no stable public JSON job feed used here).

### URL Patterns Discovered

| What | Pattern |
|---|---|
| Career root | `/careers` or `/{locale}/careers` |
| Job list endpoint A | `/SearchJobs/?jobRecordsPerPage=<n>&jobOffset=<n>` |
| Job list endpoint B | `/SearchResults/?jobRecordsPerPage=<n>&jobOffset=<n>` |
| Job detail | `/JobDetail/{slug}/{id}` or `/JobDetail?jobId={id}` |
| Apply link | `/ApplicationMethods?jobId={id}` |

Implementation notes:

- The scraper now auto-detects listing endpoint per site (`SearchJobs` or `SearchResults`).
- Pagination is controlled with `jobOffset` and continues until no new jobs are found.
- In-run dedup prevents repeated jobs while paginating.

## Pagination Limitation

Some tenants ignore higher `jobRecordsPerPage` values and return a fixed page size.

Impact:

- Large tenants require many requests.
- This is an Avature tenant/backend behavior, not a client-side bug.

## HTTP Fingerprint Strategy

This project uses `curl_cffi` (browser impersonation) to reduce blocking risk compared with plain Python HTTP fingerprints.

| Library | Fingerprint style | Block risk |
|---|---|---|
| `requests` | Generic Python | Higher |
| `httpx` | Generic Python | Higher |
| `curl_cffi` | Browser-like | Lower |

## Rate Limiting and Proxies

Proxy rotation is supported through `input/proxies.txt`:

- rotate proxies per request
- mark failing proxies as bad
- continue with healthy proxies

If `input/proxies.txt` is missing, scraper runs direct.

## Results (Latest Run)

Source: `output/stats.json` (`generated_at`: `2026-02-27T04:37:07.449479`)

- Sites processed: **121**
- Total unique jobs (after dedup): **19,953**
- Duplicates removed: **2,095**
- Total companies: **69**
- Failed sites in latest run: **0** (`output/progress.json`)

Top 10 companies by jobs:

| Company | Jobs |
|---|---:|
| Sandboxtesco | 2,010 |
| Manpowergroupco | 2,004 |
| Nva | 1,816 |
| Loa | 1,671 |
| Tesco | 1,020 |
| Deloitteus | 731 |
| Deloittecm | 616 |
| Xerox | 610 |
| Mantech | 595 |
| Advocateaurorahealth | 568 |

## Output Files

- `output/jobs.json` - all jobs with metadata:
  - `job_id`
  - `title`
  - `description`
  - `application_url`
  - `location`
  - `date_posted`
  - `company`
  - `source_url`
  - `scraped_at`
- `output/stats.json` - summary statistics
- `output/progress.json` - completed/failed sites for resume

## Submission Checklist

- Code: this repository
- Input file(s):
  - `input/avature_sites.txt`
  - `input/retry_sites.txt`
- Output file:
  - `output/jobs.json`
- Stats:
  - `output/stats.json`

Starter pack reference:
- https://drive.google.com/file/d/1XvHhurCZc4duuNYIdnehrDIsfwN8pkx3/view?usp=sharing

## Ownership

This repository and submission are property of **Ivan Alvarez**.
