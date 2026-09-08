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
import urllib.request

VOCECHAT_URL = os.getenv("VOCECHAT_URL", "https://example.com/api/v1/bot/message")
API_KEY      = os.getenv("VOCECHAT_API_KEY", "")

message = sys.argv[1] if len(sys.argv) > 1 else "Zoo Code requires your attention."

if not API_KEY:
    print("❌ VOCECHAT_API_KEY is not set.", file=sys.stderr)
    sys.exit(1)

data = json.dumps({
    "content_type": "text/markdown",
    "content": message
}).encode('utf-8')

req = urllib.request.Request(
    VOCECHAT_URL,
    data=data,
    method='POST',
    headers={
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"✅ VoceChat responded {resp.status}")
except urllib.error.HTTPError as e:
    print(f"❌ VoceChat responded {e.code}: {e.reason}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"❌ Failed to send VoceChat notification: {e}", file=sys.stderr)
    sys.exit(1)