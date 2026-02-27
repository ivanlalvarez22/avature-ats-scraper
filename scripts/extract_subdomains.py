#!/usr/bin/env python
"""Extract unique Avature subdomains from URLs file."""

import re
from pathlib import Path


def extract_unique_subdomains(input_file: str, output_file: str) -> list[str]:
    """
    Read URLs file and get unique subdomains.
    
    Args:
        input_file: Path to URLs file
        output_file: Path to save results
    
    Returns:
        List of career URLs sorted by name
    """
    subdomains = set()
    url_count = 0
    pattern = r'https?://([a-zA-Z0-9-]+)\.avature\.net'
    skip_words = ['test', 'example', 'demo', 'sandbox', 'staging', 'dev', 'qa']
    
    print(f"Reading file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            url_count += 1
            match = re.search(pattern, line.strip())
            if match:
                subdomain = match.group(1).lower()
                if not any(word in subdomain for word in skip_words):
                    subdomains.add(subdomain)
            
            if url_count % 100000 == 0:
                print(f"  Processed {url_count:,} URLs... ({len(subdomains)} unique)")
    
    print(f"\nDone:")
    print(f"  - URLs processed: {url_count:,}")
    print(f"  - Unique subdomains: {len(subdomains):,}")
    
    career_urls = [f"https://{sub}.avature.net/careers" for sub in sorted(subdomains)]
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(career_urls))
    
    print(f"\nSaved to: {output_file}")
    print(f"Total sites: {len(career_urls):,}")
    
    print(f"\nExamples:")
    for url in career_urls[:10]:
        print(f"  - {url}")
    if len(career_urls) > 10:
        print(f"  ... and {len(career_urls) - 10} more")
    
    return career_urls


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    input_file = project_root / "Urls.txt"
    output_file = project_root / "input" / "avature_sites.txt"
    
    if not input_file.exists():
        print(f"ERROR: File not found: {input_file}")
        exit(1)
    
    extract_unique_subdomains(str(input_file), str(output_file))
