"""Download REMS calibrated 'rmd' and 'adr' products (data + XML labels)
from a PDS directory listing. Standard library only.

Usage:  python download_rems.py
        python download_rems.py --dry-run
"""
import argparse
import os
import sys
import time
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

BASE = ("https://atmos.nmsu.edu/PDS/data/PDS4/msl_rems_bundle/"
        "data_calibrated/SOL_04710_04843/")
OUT_DIR = os.path.join("rems_raw", "SOL_04710_04843")
KEEP = ("rmd", "adr")          # product codes to keep
DELAY = 1.0                    # seconds between requests
UA = "rems-personal-download/1.0"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def walk(url, depth=0, max_depth=3):
    """Yield file URLs under a listing, recursing into subfolders."""
    time.sleep(DELAY)
    parser = LinkParser()
    parser.feed(fetch(url).decode("utf-8", errors="replace"))
    for href in parser.links:
        if href.startswith(("?", "#")):
            continue
        full = urljoin(url, href)
        if not full.startswith(BASE):          # skip parent directory links
            continue
        if href.endswith("/"):
            if depth < max_depth and full != url:
                yield from walk(full, depth + 1, max_depth)
        else:
            yield full


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="list matching files without downloading")
    args = ap.parse_args()

    # Respect the site's robots.txt
    host = "{0.scheme}://{0.netloc}".format(urlparse(BASE))
    rp = urllib.robotparser.RobotFileParser(host + "/robots.txt")
    rp.read()
    if not rp.can_fetch(UA, BASE):
        sys.exit("robots.txt disallows automated access to this path.\n"
                 "Download manually in a browser or contact the data curator.")

    os.makedirs(OUT_DIR, exist_ok=True)
    count = 0
    for url in walk(BASE):
        name = os.path.basename(urlparse(url).path)
        if not any(code in name.lower() for code in KEEP):
            continue
        dest = os.path.join(OUT_DIR, name)
        count += 1
        if args.dry_run:
            print("would download", url)
            continue
        if os.path.exists(dest):
            print("skip (exists)", name)
            continue
        print("downloading", name)
        time.sleep(DELAY)
        with open(dest, "wb") as f:
            f.write(fetch(url))
    print(f"done: {count} matching files")


if __name__ == "__main__":
    main()
