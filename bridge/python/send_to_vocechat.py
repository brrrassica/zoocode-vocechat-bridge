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

VOCECHAT_URL    = os.getenv("VOCECHAT_URL", "https://example.com/api/v1/bot/message")
API_KEY         = os.getenv("VOCECHAT_API_KEY", "")
REQUEST_TIMEOUT = 10
MAX_REDIRECTS   = 5

message = sys.argv[1] if len(sys.argv) > 1 else "Zoo Code requires your attention."

if not API_KEY:
    print("❌ VOCECHAT_API_KEY is not set.", file=sys.stderr)
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
    return (parts.scheme.lower(), (parts.hostname or '').lower(), port)


def make_request(url):
    return urllib.request.Request(
        url,
        data=data,
        method='POST',
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }
    )


opener = urllib.request.build_opener(NoRedirect)
target = VOCECHAT_URL

try:
    for _ in range(MAX_REDIRECTS + 1):
        try:
            with opener.open(make_request(target), timeout=REQUEST_TIMEOUT) as resp:
                print(f"✅ VoceChat responded {resp.status}")
            break
        except urllib.error.HTTPError as e:
            location = e.headers.get("Location")
            if e.code not in (301, 302, 303, 307, 308) or not location:
                print(f"❌ VoceChat responded {e.code}: {e.reason}", file=sys.stderr)
                sys.exit(1)
            next_url = urllib.parse.urljoin(target, location)
            # Never forward the API key to a different origin.
            if origin(next_url) != origin(target):
                print(
                    f"❌ Refusing to follow VoceChat redirect to a different origin: {next_url}",
                    file=sys.stderr,
                )
                sys.exit(1)
            target = next_url
    else:
        print("❌ VoceChat redirect limit exceeded", file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f"❌ Failed to send VoceChat notification: {e}", file=sys.stderr)
    sys.exit(1)