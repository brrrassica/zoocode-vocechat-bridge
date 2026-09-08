# Python Bridge — send_to_vocechat.py

Zoo Code → VoceChat notification bridge (Python version). Uses only Python's built-in `urllib` — no external dependencies.

## Requirements

- Python ≥ 3.11

## Usage

```bash
VOCECHAT_URL="https://example.com/api/v1/bot/message" \
VOCECHAT_API_KEY="sk_live_..." \
python3 send_to_vocechat.py "🧪 Test message"
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VOCECHAT_URL` | Full VoceChat bot message endpoint | Yes |
| `VOCECHAT_API_KEY` | Bot secret / API key | Yes |

## Behavior

- Sends `POST` with `Content-Type: application/json` and `x-api-key` headers.
- Body: `{"content_type": "text/markdown", "content": "<message>"}`.
- Logs success to `stdout`, errors to `stderr`, and exits non-zero on failure.
- Does **not** crash the caller on network errors.