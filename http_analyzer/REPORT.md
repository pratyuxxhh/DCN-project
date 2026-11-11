# HTTP Response Analyzer and Status Code Monitor — Project Report

## 1. System Architecture

```
 +--------+    URLs     +-----------+  status code  +------------+
 |  User  | ----------> | Analyzer  | ------------> | Classifier |
 | (CLI)  |  main.py    |analyzer.py| <------------ |classifier.py
 +--------+             +-----------+   category    +------------+
      |                       |
      | --monitor             | result dicts
      v                       v
 +-----------+  repeats  +--------------------------+
 |  Monitor  | --------> |    Logger / Reporter     |
 |monitor.py |  alerts   | reporter.py: console,    |
 +-----------+           | http_log.csv, summary,   |
                         | summary.png              |
                         +--------------------------+
```
- **main.py** reads the arguments and the URL list, then picks a mode: single pass, monitor or raw demo.
- **analyzer.py** sends each request with `requests`, times it, and pulls out the version, status, headers, body size and redirect chain. It also contains the raw `socket` demo.
- **classifier.py** maps a status code to its class and a short meaning.
- **monitor.py** loops for a set number of rounds, compares each URL's category with the previous round, and prints an ALERT when it changes.
- **reporter.py** prints colored output, appends rows to the CSV log, and builds the summary and chart.

## 2. Sample Output (real run, trimmed)
```
URL     : https://httpbin.org/status/404   [GET]
Status  : HTTP/1.1 404 Not Found  ->  Client Error
Meaning : Not Found - resource does not exist
Time    : 1622.1 ms     Body size: 0 bytes
  Content-Type   : text/html; charset=utf-8
  Set-Cookie     : absent
------------------------------------------------------------
URL     : http://google.com   [GET]
Status  : HTTP/1.1 200 OK  ->  Redirection
Meaning : Moved Permanently ... (first reply was 301, final reply 200)
  Server         : gws
  Cache-Control  : private, max-age=0
  Set-Cookie     : present
Redirect chain: 301 http://google.com/  ->  200 http://www.google.com/
------------------------------------------------------------
URL     : https://this-domain-does-not-exist-xyz.com   [GET]
Result  : NETWORK ERROR - DNS failure (domain could not be resolved)

SUMMARY REPORT  (10 requests)
Success          | 2
Redirection      | 3
Client Error     | 2
Server Error     | 2
Network Error    | 1
Average response time : 1653.1 ms
Fastest URL           : http://google.com (256.1 ms)
Slowest URL           : https://httpbin.org/redirect/2 (2321.5 ms)
```
Monitor alert example:
`ALERT: https://site.com changed from Success (200) to Server Error (503)`

Raw demo (`python main.py --raw example.com`):
```
[Status line] HTTP/1.1 200 OK
[Headers]
   Date: Wed, 11 Nov 2026 15:17:13 GMT
   Content-Type: text/html; charset=utf-8
   Connection: close
[Blank line]
[Body] first 300 characters: <!doctype html>...
```

---

## Abstract
This project is a Python tool that sends HTTP requests to a list of URLs and examines each
response. It reads the status line, headers, body size and response time, and sorts each
status code into one of the five standard classes. It follows redirect chains, handles network
failures without crashing, can re-check sites at set intervals and raise an alert when a site's
status changes, and logs every result to a CSV file and a summary report.

## Introduction
HTTP is the application-layer protocol of the Web. Every response from a server starts with a
three-digit status code that says whether the request worked. System administrators watch these
codes to spot broken links, outages and misconfigured redirects. This project builds a
simplified version of such a monitoring tool to show how HTTP works in practice.

## Objectives
1. Send GET and HEAD requests and capture the full response.
2. Show the raw text format of an HTTP message using TCP sockets.
3. Sort status codes into the 1xx–5xx classes.
4. Track redirect chains and handle network errors.
5. Monitor URLs over time and alert on changes.
6. Log results to a file and produce a summary report.

## HTTP Background
**Request format:** a request line (`GET /path HTTP/1.1`), then header lines (`Host: example.com`),
then a blank line (CRLF), then an optional body.
**Response format:** a status line (`HTTP/1.1 200 OK`), then headers, then a blank line, then the body.

| Class | Meaning | Examples |
|---|---|---|
| 1xx | Informational | 100 Continue, 101 Switching Protocols |
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirection | 301, 302, 304, 307, 308 |
| 4xx | Client Error | 400, 401, 403, 404, 429 |
| 5xx | Server Error | 500, 502, 503, 504 |

**Transport:** HTTP runs over TCP. Plain HTTP uses port 80. HTTPS uses port 443, where TLS encrypts
the HTTP data. Before any HTTP data is sent, TCP sets up the connection with a 3-way handshake
(SYN, SYN-ACK, ACK).

## System Design
The system has five modules (see the architecture diagram above). Data moves through it as a
Python dictionary for each request. This keeps the modules independent: the analyzer does not
know how the results are printed, and the reporter does not know how the requests are sent.

## Implementation
- Language: Python 3.10. Libraries: `requests`, `socket`, `argparse`, `csv`, `time`, and optionally `matplotlib`.
- Response time is measured with `time.perf_counter()` before and after the request.
- Redirects are followed automatically. `response.history` holds each intermediate 3xx response.
- Exceptions (`Timeout`, `ConnectionError`, `InvalidURL`) are caught and labelled "Network Error".
- Colors use ANSI escape codes. On Windows, `os.system("")` turns on ANSI support in the console.
- The raw demo opens `socket.create_connection((host, 80))`, sends a hand-written request ending in `\r\n\r\n`, and reads until the server closes the connection.

## Results
On the test list of 10 URLs, the tool sorted every response correctly. The httpbin status URLs
produced 2xx, 4xx and 5xx results as expected. `/redirect/2`, `/status/301` and `google.com`
showed their full redirect chains. The fake domain produced a DNS-failure Network Error, and
the program kept running. The CSV log and summary were created.

## Applications
Website uptime monitoring, finding broken links, checking redirect setups (HTTP→HTTPS) and SEO
audits, testing APIs, and teaching how the HTTP protocol works.

## Limitations
- The checks run one after another, so a long URL list is slow.
- The raw demo supports plain HTTP only (no TLS) and does not decode chunked bodies.
- There are no email or SMS alerts and no persistent database.
- Response time includes DNS lookup and TLS setup, so it is not pure server time.

## Future Scope
Concurrent requests with threads, a web dashboard using Flask, email and Telegram alerts, HTTPS
certificate-expiry checks, HTTP/2 support, and historical graphs.

## Conclusion
The project shows the HTTP request/response cycle, the meaning of status codes, and how
application-layer traffic runs on TCP. It produces a working tool for analyzing and monitoring
websites using only basic Python.

## References
1. RFC 9110 – HTTP Semantics; RFC 9112 – HTTP/1.1.
2. MDN Web Docs – HTTP response status codes.
3. Forouzan, *Data Communications and Networking*, McGraw-Hill.
4. Kurose & Ross, *Computer Networking: A Top-Down Approach*.
5. Python docs: `socket`, `argparse`, `csv`; Requests library documentation.

---

## Viva Questions
1. **301 vs 302?** 301 means the resource has moved permanently, so browsers and search engines update the link. 302 means it has moved temporarily, so clients should keep using the old URL.
2. **What does 304 mean?** Not Modified. The cached copy is still valid, so the server sends no body. This is triggered by `If-Modified-Since` or `If-None-Match`.
3. **Why use HEAD?** It returns only the headers, with no body. This makes it fast for checking whether a page exists, its size or its type.
4. **HTTP vs HTTPS?** HTTPS is HTTP sent over TLS, which provides encryption, integrity and server authentication. HTTP uses port 80 and HTTPS uses port 443.
5. **Which layer is HTTP in?** The application layer (TCP/IP model). It uses TCP at the transport layer.
6. **What is a header?** A `Name: value` line that carries metadata about the request or response, such as `Content-Type` or `Server`.
7. **What happens before HTTP data is sent?** First a DNS lookup, then the TCP 3-way handshake (SYN → SYN-ACK → ACK). For HTTPS, a TLS handshake follows.
8. **Why does HTTP use TCP and not UDP?** HTTP needs reliable, in-order delivery, and TCP provides it.
9. **What separates headers from body?** An empty line (CRLF CRLF, `\r\n\r\n`).
10. **What is the Host header for?** It names the website. This lets one IP address host many sites (virtual hosting). It is required in HTTP/1.1.
11. **401 vs 403?** 401 means you are not authenticated, so you need to log in. 403 means you are authenticated but not allowed to access the resource.
12. **502 vs 504?** 502 means the gateway got an invalid response from the upstream server. 504 means the upstream server did not respond in time.
13. **What is HTTP's statelessness?** Each request is independent. State such as a login is kept using cookies (`Set-Cookie`).
14. **307 vs 302?** A 307 redirect must keep the same method and body (a POST stays a POST). With 302, clients often change the method to GET.
15. **How do you detect a DNS failure in the code?** `requests` raises a `ConnectionError` with a name-resolution message. We catch it and label it "Network Error". No status code exists because no TCP connection was ever made.
