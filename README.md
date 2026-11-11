# DCN-project

## HTTP Response Analyzer and Status Code Monitor

This is a Python mini-project for the Data Communication and Networking course. The tool:

- sends HTTP requests (GET or HEAD) to one or more URLs
- reads the full response: HTTP version, status code, reason phrase, key headers, response time and body size
- sorts each status code into a class: **1xx** Informational, **2xx** Success, **3xx** Redirection, **4xx** Client Error or **5xx** Server Error
- shows the full redirect chain (for example `301 → 200`)
- handles timeouts, DNS failures, refused connections and invalid URLs, labelling them **Network Error** instead of crashing
- re-checks URLs every N seconds in monitoring mode and prints an **ALERT** when a URL's category changes
- logs every result to `http_log.csv` and prints a summary report, and can also save a bar chart (`summary.png`)
- includes a raw `socket` demo that sends a hand-written HTTP/1.1 request over TCP port 80, so you can see the real message format

The code is in [http_analyzer/](http_analyzer/). The project report and viva questions are in [http_analyzer/REPORT.md](http_analyzer/REPORT.md).

## Requirements
- Python 3.10+
- `requests`, plus `matplotlib` if you want the chart

```bash
cd http_analyzer
python -m pip install -r requirements.txt
```

## Command Manual

Run every command from inside the `http_analyzer` folder.

| Command | What it does |
|---|---|
| `python main.py --url https://example.com` | Analyze a single URL |
| `python main.py --url URL1 --url URL2` | Analyze several URLs (repeat `--url`) |
| `python main.py --url https://example.com --method HEAD` | Use HEAD instead of GET (headers only) |
| `python main.py --file urls.txt` | Analyze every URL in a file (one per line; lines starting with `#` are ignored) |
| `python main.py --file urls.txt --monitor --interval 10 --rounds 5` | Re-check all URLs every 10 s for 5 rounds and alert on changes |
| `python main.py --raw example.com` | Raw socket demo: shows the status line, headers, blank line and body |
| `python main.py --file urls.txt --no-chart` | Skip creating `summary.png` |
| `python main.py --help` | Show all options |

### Options
| Option | Default | Description |
|---|---|---|
| `--url URL` | – | URL to analyze; can be given more than once |
| `--file PATH` | – | Text file with URLs |
| `--method GET\|HEAD` | `GET` | HTTP method |
| `--monitor` | off | Turn on monitoring mode |
| `--interval N` | `10` | Seconds between monitoring rounds |
| `--rounds N` | `3` | Number of monitoring rounds |
| `--raw HOST` | – | Raw TCP/HTTP demo on port 80 |
| `--no-chart` | off | Do not save the bar chart |

Press `Ctrl+C` to stop at any time.

## Output
- **Console colors:** green = 2xx, yellow = 3xx, magenta = 4xx, red = 5xx, grey = network error
- **`http_log.csv`:** timestamp, url, method, status_code, category, reason, response_time_ms, content_type, size_bytes
- **Summary:** count for each category, average response time, and the fastest and slowest URL
- **`summary.png`:** bar chart of the category counts (only if matplotlib is installed)
