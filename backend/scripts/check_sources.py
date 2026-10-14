"""Checks each URL in services.yaml and channels.yaml: status, final host after
redirects, and whether robots.txt allows fetching. Polite: one request per URL,
1 second apart. Run from backend/:  python scripts/check_sources.py
"""
import time
import urllib.robotparser as rp
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import yaml

DATA = Path(__file__).resolve().parents[1] / "app" / "data"
UA = "CivicAssistantStudentProject/0.1 (source verification)"


def collect_urls() -> list[str]:
    urls = []
    for fname, key, field in (
        ("services.yaml", "services", "official_url"),
        ("channels.yaml", "channels", "url"),
    ):
        data = yaml.safe_load((DATA / fname).read_text(encoding="utf-8"))
        urls += [i[field] for i in data[key] if i.get(field)]
    return sorted(set(urls))


def robots_for(client: httpx.Client, url: str) -> rp.RobotFileParser:
    parts = urlsplit(url)
    parser = rp.RobotFileParser()
    try:
        r = client.get(f"{parts.scheme}://{parts.netloc}/robots.txt")
        parser.parse(r.text.splitlines() if r.status_code == 200 else [])
    except httpx.HTTPError:
        parser.parse([])
    return parser


def main() -> None:
    with httpx.Client(
        headers={"User-Agent": UA}, timeout=15, follow_redirects=True
    ) as client:
        for url in collect_urls():
            try:
                robots_ok = robots_for(client, url).can_fetch(UA, url)
                time.sleep(1)
                r = client.get(url)
                final = urlsplit(str(r.url)).netloc
                print(f"{r.status_code} robots_ok={robots_ok} final_host={final}\n  {url}")
            except httpx.HTTPError as e:
                print(f"ERROR {type(e).__name__}\n  {url}")
            time.sleep(1)


if __name__ == "__main__":
    main()