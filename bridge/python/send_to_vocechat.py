#!/usr/bin/env python3
# send_to_vocechat.py
# Zoo Code -> VoceChat notification bridge (Python version)
# Usage: python3 send_to_vocechat.py "<your message>"
#
# Reads configuration from environment variables:
#   VOCECHAT_URL      - full VoceChat bot message endpoint
#   VOCECHAT_API_KEY  - bot secret / API key
import os
import sys
import json
import urllib.error
import urllib.parse
import urllib.request

VOCECHAT_URL    = os.getenv("VOCECHAT_URL", "")
API_KEY         = os.getenv("VOCECHAT_API_KEY", "")
REQUEST_TIMEOUT = 10
MAX_REDIRECTS   = 5

message = sys.argv[1] if len(sys.argv) > 1 else "Zoo Code requires your attention."

if not API_KEY:
    print("❌ VOCECHAT_API_KEY is not set.", file=sys.stderr)
    sys.exit(1)

if not VOCECHAT_URL:
    print("❌ VOCECHAT_URL is not set.", file=sys.stderr)
    sys.exit(1)

def normalize_host(host):
    # A trailing dot is the same absolute DNS name, so strip it before any
    # host comparison or request.
    return (host or "").lower().rstrip(".")


def normalize_url(parts):
    # Rebuild the URL with a normalized hostname so absolute FQDNs with a
    # trailing dot still pass TLS hostname verification.
    host = normalize_host(parts.hostname)
    if ":" in host:
        host = f"[{host}]"
    netloc = host
    port = parts.port
    if port is not None:
        netloc = f"{netloc}:{port}"
    if parts.username is not None:
        userinfo = parts.username
        if parts.password is not None:
            userinfo = f"{userinfo}:{parts.password}"
        netloc = f"{userinfo}@{netloc}"
    return urllib.parse.urlunsplit(
        (parts.scheme, netloc, parts.path, parts.query, parts.fragment)
    )


try:
    parsed_url = urllib.parse.urlsplit(VOCECHAT_URL)
    url_host = normalize_host(parsed_url.hostname)
    target = normalize_url(parsed_url)
except ValueError as e:
    print(f"❌ Invalid VOCECHAT_URL: {e}", file=sys.stderr)
    sys.exit(1)

if parsed_url.scheme.lower() not in ("http", "https"):
    print("❌ VOCECHAT_URL must use http or https.", file=sys.stderr)
    sys.exit(1)

if not url_host:
    print("❌ VOCECHAT_URL must include a hostname.", file=sys.stderr)
    sys.exit(1)

if url_host == "example.com" or url_host.endswith(".example.com"):
    print("❌ VOCECHAT_URL still points at the example.com placeholder.", file=sys.stderr)
    sys.exit(1)

data = json.dumps({
    "content_type": "text/markdown",
    "content": message
}).encode('utf-8')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def origin(url):
    parts = urllib.parse.urlsplit(url)
    port = parts.port or (443 if parts.scheme == 'https' else 80)
    return (parts.scheme.lower(), normalize_host(parts.hostname), port)


def make_request(url, method='POST', data=data):
    headers = {"x-api-key": API_KEY}
    if data is not None:
        headers["Content-Type"] = "application/json"
    return urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=headers
    )


opener = urllib.request.build_opener(NoRedirect)
method = 'POST'
body = data

try:
    for _ in range(MAX_REDIRECTS + 1):
        try:
            with opener.open(make_request(target, method=method, data=body), timeout=REQUEST_TIMEOUT) as resp:
                # Consume the body so a truncated or reset reply raises
                # (e.g. http.client.IncompleteRead) instead of being counted
                # as delivered.
                resp.read()
                if resp.status is not None and 200 <= resp.status < 300:
                    print(f"✅ VoceChat responded {resp.status}")
                else:
                    print(f"❌ VoceChat responded {resp.status}", file=sys.stderr)
                    sys.exit(1)
            break
        except urllib.error.HTTPError as e:
            location = e.headers.get("Location")
            if e.code not in (301, 302, 303, 307, 308) or not location:
                print(f"❌ VoceChat responded {e.code}: {e.reason}", file=sys.stderr)
                sys.exit(1)
            next_url = normalize_url(
                urllib.parse.urlsplit(urllib.parse.urljoin(target, location))
            )
            # Never forward the API key to a different origin.
            if origin(next_url) != origin(target):
                print(
                    f"❌ Refusing to follow VoceChat redirect to a different origin: {next_url}",
                    file=sys.stderr,
                )
                sys.exit(1)
            # 303 See Other (and legacy 301/302) is followed with a bodyless
            # GET; 307/308 repeat the current method and body.
            if e.code in (301, 302, 303):
                method = 'GET'
                body = None
            target = next_url
    else:
        print("❌ VoceChat redirect limit exceeded", file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f"❌ Failed to send VoceChat notification: {e}", file=sys.stderr)
    sys.exit(1)