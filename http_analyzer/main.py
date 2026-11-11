"""
main.py
-------
Entry point of the HTTP Response Analyzer and Status Code Monitor.

Usage:
    python main.py --url https://example.com
    python main.py --file urls.txt
    python main.py --file urls.txt --monitor --interval 10 --rounds 5
    python main.py --raw example.com
    python main.py --url https://example.com --method HEAD
"""

import argparse
import sys

from analyzer import analyze_url, raw_http_demo
from monitor import monitor_urls
from reporter import print_result, log_results, print_summary


def read_urls_from_file(path):
    """Read one URL per line; skip blank lines and lines starting with #."""
    urls = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
    except FileNotFoundError:
        print("Error: file not found:", path)
        sys.exit(1)
    return urls


def build_parser():
    parser = argparse.ArgumentParser(
        description="HTTP Response Analyzer and Status Code Monitor")
    parser.add_argument("--url", action="append",
                        help="URL to analyse (can be given more than once)")
    parser.add_argument("--file", help="text file with one URL per line")
    parser.add_argument("--method", default="GET", choices=["GET", "HEAD"],
                        help="HTTP method to use (default GET)")
    parser.add_argument("--monitor", action="store_true",
                        help="re-check URLs periodically")
    parser.add_argument("--interval", type=int, default=10,
                        help="seconds between monitor rounds (default 10)")
    parser.add_argument("--rounds", type=int, default=3,
                        help="number of monitor rounds (default 3)")
    parser.add_argument("--raw", metavar="HOST",
                        help="raw socket demo: send a hand-written GET to HOST:80")
    parser.add_argument("--no-chart", action="store_true",
                        help="do not create summary.png")
    return parser


def main():
    args = build_parser().parse_args()

    # 1) Raw socket demo is a separate mode.
    if args.raw:
        raw_http_demo(args.raw)
        return

    # 2) Collect URLs from --url and/or --file.
    urls = []
    if args.url:
        urls.extend(args.url)
    if args.file:
        urls.extend(read_urls_from_file(args.file))
    if not urls:
        print("No URLs given. Use --url, --file or --raw. Try: python main.py --help")
        sys.exit(1)

    # 3) Monitoring mode or single pass.
    if args.monitor:
        results = monitor_urls(urls, args.method, args.interval, args.rounds)
    else:
        results = []
        for url in urls:
            r = analyze_url(url, args.method)
            print_result(r)
            results.append(r)
        log_results(results)

    # 4) Final summary.
    print_summary(results, make_chart=not args.no_chart)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
