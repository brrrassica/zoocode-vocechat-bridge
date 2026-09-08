# Zoo Code → VoceChat Notification Bridge

A small, dependency-light bridge that POSTs notifications from Zoo Code to a VoceChat chat via its inbound webhook API.

**Target endpoint:** `https://example.com/api/v1/bot/message`

## Implementations

Both implementations are functionally identical and read the same environment variables. Choose whichever runtime you prefer.

| Directory | Language | Runtime | File |
|-----------|----------|---------|------|
| [`bridge/node/`](bridge/node/README.md) | Node.js | Node ≥ 18 | `send_to_vocechat.js` |
| [`bridge/python/`](bridge/python/README.md) | Python | Python ≥ 3.11 | `send_to_vocechat.py` |

## Quick Start

1. **Install** Node (≥ 18) or Python (≥ 3.11).
2. **Configure** your credentials:
   ```bash
   cp .env.example .env
   # edit .env and set VOCECHAT_URL and VOCECHAT_API_KEY
   ```
3. **Test** the bridge:
   ```bash
   # Node
   set -a && source .env && set +a
   node bridge/node/send_to_vocechat.js "🧪 Test message"

   # Python
   set -a && source .env && set +a
   python3 bridge/python/send_to_vocechat.py "🧪 Test message"
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VOCECHAT_URL` | Full VoceChat bot message endpoint | Yes |
| `VOCECHAT_API_KEY` | Bot secret / API key | Yes |

## Payload

Both scripts send the same JSON body:

```json
{
  "content_type": "text/markdown",
  "content": "<the message text>"
}
```
