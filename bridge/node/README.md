# Node Bridge — send_to_vocechat.js

Zoo Code → VoceChat notification bridge (Node version). Uses only Node's built-in `https` module — no external dependencies.

## Requirements

- Node.js ≥ 18

## Usage

```bash
VOCECHAT_URL="https://example.com/api/v1/bot/message" \
VOCECHAT_API_KEY="sk_live_..." \
node send_to_vocechat.js "🧪 Test message"
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