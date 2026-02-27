"""Deduplicate jobs and generate final stats."""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter


def main():
    """Load jobs, deduplicate, and generate stats."""
    jobs_file = Path("output/jobs.json")
    
    with open(jobs_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    jobs = data.get("jobs", [])
    print(f"Total jobs before dedup: {len(jobs)}")
    
    seen_ids = set()
    unique_jobs = []
    
    for job in jobs:
        job_id = job.get("job_id")
        if job_id and job_id not in seen_ids:
            seen_ids.add(job_id)
            unique_jobs.append(job)
    
    print(f"Total jobs after dedup: {len(unique_jobs)}")
    print(f"Duplicates removed: {len(jobs) - len(unique_jobs)}")
    
    companies = Counter(job.get("company", "Unknown") for job in unique_jobs)
    top_companies = companies.most_common(10)
    
    locations = Counter(job.get("location", "Unknown") for job in unique_jobs)
    top_locations = locations.most_common(10)
    
    stats = {
        "total_jobs": len(unique_jobs),
        "total_companies": len(companies),
        "duplicates_removed": len(jobs) - len(unique_jobs),
        "top_companies": [{"company": c, "jobs": n} for c, n in top_companies],
        "top_locations": [{"location": l, "jobs": n} for l, n in top_locations],
        "generated_at": datetime.now().isoformat()
    }
    
    with open("output/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print("\nSaved: output/stats.json")
    
    final_data = {
        "total_jobs": len(unique_jobs),
        "stats": stats,
        "jobs": unique_jobs
    }
    
    with open(jobs_file, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2)
    print(f"Saved: {jobs_file}")
    
    print("\n=== TOP 10 COMPANIES ===")
    for company, count in top_companies:
        print(f"  {company}: {count} jobs")
    
    print("\n=== TOP 10 LOCATIONS ===")
    for location, count in top_locations:
        print(f"  {location}: {count} jobs")


if __name__ == "__main__":
    main()
