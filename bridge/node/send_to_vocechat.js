#!/usr/bin/env node
// send_to_vocechat.js
// Zoo Code -> VoceChat notification bridge (Node version)
// Usage: node send_to_vocechat.js "<your message>"
//
// Reads configuration from environment variables:
//   VOCECHAT_URL      - full VoceChat bot message endpoint
//   VOCECHAT_API_KEY  - bot secret / API key
const http = require('http');
const https = require('https');

const VOCECHAT_URL = process.env.VOCECHAT_URL || "https://example.com/api/v1/bot/message";
const API_KEY      = process.env.VOCECHAT_API_KEY || "";

const message = process.argv[2] ?? "Zoo Code requires your attention.";

if (!API_KEY) {
  console.error('❌ VOCECHAT_API_KEY is not set.');
  process.exit(1);
}

const payload = JSON.stringify({
  content_type: "text/markdown",
  content: message
});

const url = new URL(VOCECHAT_URL);

// URL.hostname keeps the brackets on IPv6 literals, but net.connect expects
// the bare address (e.g. "::1" rather than "[::1]").
const hostname = url.hostname.startsWith('[')
  ? url.hostname.slice(1, -1)
  : url.hostname;

const options = {
  method: 'POST',
  hostname,
  port: url.port || undefined,
  path: url.pathname + url.search,
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': API_KEY,
    'Content-Length': Buffer.byteLength(payload)
  }
};

const transport = url.protocol === 'http:' ? http : https;

const req = transport.request(options, (res) => {
  res.on('data', () => {}); // drain
  res.on('end', () => {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      console.log(`✅ VoceChat responded ${res.statusCode}`);
    } else {
      console.error(`❌ VoceChat responded ${res.statusCode}`);
      process.exit(1);
    }
  });
});

req.on('error', (err) => {
  console.error('❌ Failed to send VoceChat notification:', err.message);
  process.exit(1);
});

req.setTimeout(10000, () => {
  req.destroy(new Error('VoceChat request timed out'));
});

req.write(payload);
req.end();