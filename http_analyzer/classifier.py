"""
classifier.py
-------------
Classifies HTTP status codes into their five standard classes
and gives a short meaning for well-known codes.

Status code classes (RFC 9110):
    1xx -> Informational
    2xx -> Success
    3xx -> Redirection
    4xx -> Client Error
    5xx -> Server Error
"""

# A dictionary of about 20 well-known status codes and their meanings.
STATUS_MEANINGS = {
    100: "Continue - client may send the request body",
    101: "Switching Protocols - e.g. upgrade to WebSocket",
    200: "OK - request succeeded",
    201: "Created - a new resource was created",
    204: "No Content - success, but no body returned",
    301: "Moved Permanently - resource has a new permanent URL",
    302: "Found - resource temporarily at another URL",
    304: "Not Modified - use your cached copy",
    307: "Temporary Redirect - same method must be reused",
    308: "Permanent Redirect - same method must be reused",
    400: "Bad Request - server could not understand the request",
    401: "Unauthorized - authentication is required",
    403: "Forbidden - server refuses to allow access",
    404: "Not Found - resource does not exist",
    405: "Method Not Allowed - this HTTP method is not supported",
    429: "Too Many Requests - client is being rate limited",
    500: "Internal Server Error - generic server failure",
    502: "Bad Gateway - invalid response from upstream server",
    503: "Service Unavailable - server overloaded or down",
    504: "Gateway Timeout - upstream server did not respond in time",
}

# Category name used when no HTTP response was received at all.
NETWORK_ERROR = "Network Error"


def classify_status(code):
    """
    Return a tuple (category, meaning) for an HTTP status code.

    Example:
        classify_status(404) -> ("Client Error", "Not Found - resource does not exist")
    """
    # If there is no code, the request never got a response.
    if code is None:
        return NETWORK_ERROR, "No response received (timeout, DNS or connection failure)"

    # The first digit of the code decides the class.
    if 100 <= code <= 199:
        category = "Informational"
    elif 200 <= code <= 299:
        category = "Success"
    elif 300 <= code <= 399:
        category = "Redirection"
    elif 400 <= code <= 499:
        category = "Client Error"
    elif 500 <= code <= 599:
        category = "Server Error"
    else:
        category = "Unknown"

    # Look up a meaning; use a generic text if the code is not in our table.
    meaning = STATUS_MEANINGS.get(code, "No description available for this code")
    return category, meaning
