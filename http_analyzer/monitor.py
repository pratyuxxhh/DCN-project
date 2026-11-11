"""
monitor.py
----------
Monitoring mode: re-check every URL every N seconds for a fixed number
of rounds and print an ALERT when a URL's status category changes.
"""

import time

from analyzer import analyze_url
from reporter import print_result, log_results, RED, RESET


def describe(result):
    """Short text such as 'Success (200)' or 'Network Error'."""
    if result["status_code"] is None:
        return result["category"]
    return "%s (%d)" % (result["category"], result["status_code"])


def monitor_urls(urls, method, interval, rounds):
    """Run the monitoring loop and return every result collected."""
    all_results = []
    last_seen = {}    # url -> result from the previous round

    for round_no in range(1, rounds + 1):
        print()
        print("#" * 60)
        print("MONITOR ROUND %d of %d" % (round_no, rounds))
        print("#" * 60)

        round_results = []
        for url in urls:
            r = analyze_url(url, method)
            print_result(r)
            round_results.append(r)

            # Compare with the previous round for the same URL.
            if url in last_seen:
                old = last_seen[url]
                if old["category"] != r["category"]:
                    print(RED + "ALERT: %s changed from %s to %s"
                          % (url, describe(old), describe(r)) + RESET)
            last_seen[url] = r

        log_results(round_results)
        all_results.extend(round_results)

        # Wait before the next round (but not after the last one).
        if round_no < rounds:
            print("\nWaiting %d seconds... (Ctrl+C to stop)" % interval)
            time.sleep(interval)

    return all_results
