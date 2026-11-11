"""
analyzer.py
-----------
Sends HTTP requests, measures them and extracts the useful parts
of each HTTP response. Also contains a raw socket demo that shows
the real text format of an HTTP message.
"""

import socket
import time
from datetime import datetime

import requests

from classifier import classify_status, NETWORK_ERROR

TIMEOUT_SECONDS = 5

# Headers we want to show for every response.
KEY_HEADERS = ["Content-Type", "Content-Length", "Server", "Date",
               "Location", "Cache-Control"]


def http_version_text(raw_version):
    """requests stores the version as a number: 10 -> HTTP/1.0, 11 -> HTTP/1.1."""
    if raw_version == 10:
        return "HTTP/1.0"
    if raw_version == 11:
        return "HTTP/1.1"
    if raw_version == 20:
        return "HTTP/2"
    return "HTTP/?"


def analyze_url(url, method="GET"):
    """
    Send one HTTP request and return a dictionary describing the result.
    This function never raises an exception: network problems are
    returned as category "Network Error".
    """
    # Add http:// if the user forgot the scheme (e.g. "example.com").
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "method": method,
        "http_version": "",
        "status_code": None,
        "reason": "",
        "category": NETWORK_ERROR,
        "meaning": "",
        "headers": {},
        "set_cookie": "absent",
        "response_time_ms": 0.0,
        "size_bytes": 0,
        "content_type": "",
        "redirects": [],   # list of (status_code, url) for each hop
        "error": "",
    }

    start = time.perf_counter()   # high-resolution timer
    try:
        # allow_redirects=True makes requests follow 3xx automatically,
        # and the earlier hops are stored in response.history.
        response = requests.request(method, url, timeout=TIMEOUT_SECONDS,
                                    allow_redirects=True)
    except requests.exceptions.Timeout:
        result["error"] = "Timeout (no reply within %d s)" % TIMEOUT_SECONDS
    except requests.exceptions.ConnectionError as e:
        # DNS failure and "connection refused" both arrive here.
        text = str(e)
        if "getaddrinfo" in text or "Name or service not known" in text or "NameResolution" in text:
            result["error"] = "DNS failure (domain could not be resolved)"
        elif "refused" in text.lower():
            result["error"] = "Connection refused"
        else:
            result["error"] = "Connection error"
    except (requests.exceptions.InvalidURL, requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema):
        result["error"] = "Invalid URL"
    except requests.exceptions.RequestException as e:
        result["error"] = "Request failed: " + type(e).__name__

    elapsed_ms = (time.perf_counter() - start) * 1000
    result["response_time_ms"] = round(elapsed_ms, 1)

    # If an error happened, fill the meaning and stop here.
    if result["error"]:
        category, meaning = classify_status(None)
        result["meaning"] = meaning
        return result

    # ---- We got a response: extract the parts of the HTTP message ----
    result["http_version"] = http_version_text(response.raw.version)
    result["status_code"] = response.status_code
    result["reason"] = response.reason
    category, meaning = classify_status(response.status_code)
    result["category"] = category
    result["meaning"] = meaning

    # Collect the key headers (header names are case-insensitive).
    for name in KEY_HEADERS:
        if name in response.headers:
            result["headers"][name] = response.headers[name]
    if "Set-Cookie" in response.headers:
        result["set_cookie"] = "present"

    result["content_type"] = response.headers.get("Content-Type", "")
    result["size_bytes"] = len(response.content)   # 0 for HEAD requests

    # Redirect chain: every response in history was a 3xx hop.
    for hop in response.history:
        result["redirects"].append((hop.status_code, hop.url))
    if response.history:
        result["redirects"].append((response.status_code, response.url))
        # The URL we asked for answered with a 3xx, so we count it as a
        # Redirection (the final status is still shown in the chain).
        first_code = response.history[0].status_code
        category, meaning = classify_status(first_code)
        result["category"] = category
        result["meaning"] = "%s (first reply was %d, final reply %d)" % (
            meaning, first_code, response.status_code)

    return result


def raw_http_demo(host, path="/"):
    """
    Open a plain TCP connection to port 80, send a hand-written
    HTTP/1.1 GET request and print the raw response text.
    This shows the real structure of an HTTP message:
        status line -> headers -> blank line -> body
    """
    port = 80
    # An HTTP request is just text. Each line ends with CRLF (\r\n)
    # and an empty line marks the end of the headers.
    request_text = (
        "GET " + path + " HTTP/1.1\r\n"
        "Host: " + host + "\r\n"
        "User-Agent: DCN-Mini-Project/1.0\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    print("=" * 60)
    print("RAW HTTP DEMO: connecting to %s on TCP port %d" % (host, port))
    print("=" * 60)
    print("---- REQUEST SENT ----")
    print(request_text.replace("\r\n", "\n"))   # \r\n shown as normal newlines

    try:
        # socket.create_connection does DNS lookup + TCP 3-way handshake.
        sock = socket.create_connection((host, port), timeout=TIMEOUT_SECONDS)
        sock.sendall(request_text.encode("ascii"))

        # Read until the server closes the connection.
        chunks = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
        sock.close()
    except OSError as e:
        print("Network Error:", e)
        return

    raw = b"".join(chunks).decode("utf-8", errors="replace")

    # Split headers and body at the first blank line.
    head, _, body = raw.partition("\r\n\r\n")
    lines = head.split("\r\n")

    print("---- RESPONSE RECEIVED ----")
    print("[Status line] " + lines[0])
    print("[Headers]")
    for line in lines[1:]:
        print("   " + line)
    print("[Blank line]")
    print("[Body] first 300 characters:")
    print(body[:300])
    print("... (%d bytes total in body)" % len(body.encode("utf-8")))
