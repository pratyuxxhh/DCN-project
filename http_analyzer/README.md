# HTTP Response Analyzer and Status Code Monitor

A Data Communication and Networking mini-project in Python. It sends HTTP requests,
reads each full response (status line, headers and body), sorts the status code into a class
(1xx–5xx), follows redirects, watches URLs over time, and writes everything to a CSV log
and a summary report.

## Files
| File | Purpose |
|---|---|
| `main.py` | Command-line entry point (argparse) |
| `analyzer.py` | Sends GET/HEAD requests, extracts response details, raw socket demo |
| `classifier.py` | `classify_status(code)` and a table of 20 common codes |
| `monitor.py` | Re-checks URLs every N seconds and prints an alert when a category changes |
| `reporter.py` | Colored output, `http_log.csv`, summary table, `summary.png` |
| `urls.txt` | Test URLs that cover every category |

## Install
```bash
python -m pip install -r requirements.txt     # requests (+ optional matplotlib)
```

## Run
```bash
python main.py --url https://example.com
python main.py --url https://example.com --method HEAD
python main.py --file urls.txt
python main.py --file urls.txt --monitor --interval 10 --rounds 5
python main.py --raw example.com
```

## Output
- Colored console output: green = 2xx, yellow = 3xx, magenta = 4xx, red = 5xx, grey = network error
- `http_log.csv`: timestamp, url, method, status_code, category, reason, response_time_ms, content_type, size_bytes
- `summary.png`: bar chart of category counts (only if matplotlib is installed)

## Notes
- A URL that redirects counts as **Redirection**. The full chain (for example `301 → 200`) is printed.
- Timeouts, DNS failures, refused connections and invalid URLs are labelled **Network Error**. They do not crash the program.
- The `--raw` demo uses plain TCP on port 80, so it only works with sites that still answer plain HTTP.
