#!/usr/bin/env python
"""Validate Avature sites and optionally add from crt.sh."""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm


def get_subdomains_from_crt() -> set[str]:
    """Get extra subdomains from Certificate Transparency logs."""
    url = "https://crt.sh/?q=%.avature.net&output=json"
    subdomains = set()
    
    print("Fetching subdomains from crt.sh...")
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            certs = response.json()
            for cert in certs:
                name = cert.get("name_value", "")
                for line in name.split("\n"):
                    if ".avature.net" in line:
                        sub = line.strip().replace("*.", "").split(".avature.net")[0]
                        if sub and "test" not in sub.lower():
                            subdomains.add(sub.lower())
            print(f"  Found {len(subdomains)} subdomains from crt.sh")
    except Exception as e:
        print(f"  Error fetching crt.sh: {e}")
    
    return subdomains


def validate_site(url: str) -> tuple[str, bool, int]:
    """Check if a site is active and valid."""
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        is_valid = response.status_code == 200 and "avature" in response.text.lower()
        return (url, is_valid, response.status_code)
    except:
        return (url, False, 0)


def validate_all(urls: list[str], workers: int = 30) -> list[str]:
    """Validate many sites in parallel."""
    valid = []
    failed = []
    
    print(f"\nValidating {len(urls)} sites with {workers} workers...")
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(validate_site, url): url for url in urls}
        
        for future in tqdm(as_completed(futures), total=len(urls), desc="Validating"):
            url, is_valid, status = future.result()
            if is_valid:
                valid.append(url)
            else:
                failed.append((url, status))
    
    print(f"\n  Valid sites: {len(valid)}")
    print(f"  Failed sites: {len(failed)}")
    
    return sorted(valid)


def load_sites(filepath: str) -> list[str]:
    """Load sites from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def save_sites(filepath: str, sites: list[str]) -> None:
    """Save sites to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sites))


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    sites_file = project_root / "input" / "avature_sites.txt"
    
    existing_sites = load_sites(str(sites_file))
    print(f"Loaded {len(existing_sites)} sites from file")
    
    existing_subdomains = set()
    for url in existing_sites:
        sub = url.split("//")[1].split(".")[0]
        existing_subdomains.add(sub)
    
    crt_subdomains = get_subdomains_from_crt()
    new_subdomains = crt_subdomains - existing_subdomains
    
    if new_subdomains:
        print(f"  New subdomains from crt.sh: {len(new_subdomains)}")
        for sub in new_subdomains:
            existing_sites.append(f"https://{sub}.avature.net/careers")
        existing_sites = sorted(set(existing_sites))
        print(f"  Total sites to validate: {len(existing_sites)}")
    
    valid_sites = validate_all(existing_sites)
    
    save_sites(str(sites_file), valid_sites)
    print(f"\nSaved {len(valid_sites)} valid sites to {sites_file}")
    
    print("\nExamples of valid sites:")
    for url in valid_sites[:10]:
        print(f"  - {url}")
    if len(valid_sites) > 10:
        print(f"  ... and {len(valid_sites) - 10} more")


if __name__ == "__main__":
    main()
