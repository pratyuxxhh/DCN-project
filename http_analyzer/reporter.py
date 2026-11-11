"""
reporter.py
-----------
Everything related to output:
  * colored console printing
  * CSV logging (http_log.csv)
  * final summary report and optional bar chart (summary.png)
"""

import csv
import os

# ---- ANSI color codes (work in Linux terminals and Windows 10+ terminals) ----
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
CYAN = "\033[96m"
GREY = "\033[90m"
RESET = "\033[0m"

# On Windows, os.system("") switches on ANSI color support in the console.
if os.name == "nt":
    os.system("")

CATEGORY_COLORS = {
    "Informational": CYAN,
    "Success": GREEN,
    "Redirection": YELLOW,
    "Client Error": MAGENTA,
    "Server Error": RED,
    "Network Error": GREY,
}

LOG_FILE = "http_log.csv"
CSV_COLUMNS = ["timestamp", "url", "method", "status_code", "category", "reason",
               "response_time_ms", "content_type", "size_bytes"]


def color_for(category):
    return CATEGORY_COLORS.get(category, RESET)


def print_result(r):
    """Print one analysed response in a readable, colored block."""
    c = color_for(r["category"])
    print("-" * 60)
    print("URL     : " + r["url"] + "   [" + r["method"] + "]")
    if r["status_code"] is None:
        print(c + "Result  : NETWORK ERROR - " + r["error"] + RESET)
        print("Time    : %.1f ms" % r["response_time_ms"])
        return

    print(c + "Status  : %s %d %s  ->  %s" % (r["http_version"], r["status_code"],
                                             r["reason"], r["category"]) + RESET)
    print("Meaning : " + r["meaning"])
    print("Time    : %.1f ms     Body size: %d bytes" % (r["response_time_ms"], r["size_bytes"]))
    for name, value in r["headers"].items():
        print("  %-15s: %s" % (name, value))
    print("  %-15s: %s" % ("Set-Cookie", r["set_cookie"]))

    if r["redirects"]:
        # Build a chain like: 302 http://a -> 302 http://b -> 200 https://c
        parts = []
        for code, url in r["redirects"]:
            parts.append("%d %s" % (code, url))
        print(YELLOW + "Redirect chain: " + "  ->  ".join(parts) + RESET)


def log_results(results):
    """Append results to http_log.csv (header row is written only once)."""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(CSV_COLUMNS)
        for r in results:
            writer.writerow([
                r["timestamp"], r["url"], r["method"],
                r["status_code"] if r["status_code"] is not None else "",
                r["category"], r["reason"] or r["error"],
                r["response_time_ms"], r["content_type"], r["size_bytes"],
            ])


def print_summary(results, make_chart=True):
    """Print counts per category, average/fastest/slowest response time."""
    if not results:
        print("No results to summarise.")
        return

    order = ["Informational", "Success", "Redirection", "Client Error",
             "Server Error", "Network Error"]
    counts = {}
    for name in order:
        counts[name] = 0
    for r in results:
        counts[r["category"]] = counts.get(r["category"], 0) + 1

    print()
    print("=" * 60)
    print("SUMMARY REPORT  (%d requests)" % len(results))
    print("=" * 60)
    print("%-16s | %s" % ("Category", "Count"))
    print("-" * 26)
    for name in order:
        print(color_for(name) + "%-16s | %d" % (name, counts[name]) + RESET)

    # Timing statistics only make sense for requests that got a response.
    answered = [r for r in results if r["status_code"] is not None]
    if answered:
        total = 0
        for r in answered:
            total += r["response_time_ms"]
        average = total / len(answered)
        fastest = min(answered, key=lambda r: r["response_time_ms"])
        slowest = max(answered, key=lambda r: r["response_time_ms"])
        print("-" * 26)
        print("Average response time : %.1f ms" % average)
        print("Fastest URL           : %s (%.1f ms)" % (fastest["url"], fastest["response_time_ms"]))
        print("Slowest URL           : %s (%.1f ms)" % (slowest["url"], slowest["response_time_ms"]))
    print("Results logged to     : " + LOG_FILE)

    if make_chart:
        save_chart(counts)


def save_chart(counts):
    """Optional: draw a bar chart with matplotlib if it is installed."""
    try:
        import matplotlib
        matplotlib.use("Agg")          # draw to a file, no window needed
        import matplotlib.pyplot as plt
    except ImportError:
        print("(matplotlib not installed - skipping summary.png)")
        return

    names = list(counts.keys())
    values = list(counts.values())
    colors = ["#17becf", "#2ca02c", "#e6b800", "#c71585", "#d62728", "#7f7f7f"]

    plt.figure(figsize=(8, 4))
    plt.bar(names, values, color=colors[:len(names)])
    plt.title("HTTP Response Categories")
    plt.ylabel("Number of responses")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig("summary.png")
    plt.close()
    print("Bar chart saved to    : summary.png")
