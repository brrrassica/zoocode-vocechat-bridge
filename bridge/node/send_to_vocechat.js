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

const VOCECHAT_URL = process.env.VOCECHAT_URL;
const API_KEY      = process.env.VOCECHAT_API_KEY || "";

const message = process.argv[2] ?? "Zoo Code requires your attention.";

if (!API_KEY) {
  console.error('❌ VOCECHAT_API_KEY is not set.');
  process.exit(1);
}

if (!VOCECHAT_URL) {
  console.error('❌ VOCECHAT_URL is not set.');
  process.exit(1);
}

const MAX_REDIRECTS = 5;
const REDIRECT_STATUSES = new Set([301, 302, 303, 307, 308]);

// A trailing dot is the same absolute DNS name, so strip it (and lowercase)
// before any host comparison.
function normalizeHostname(hostname) {
  return hostname.toLowerCase().replace(/\.$/, '');
}

function origin(parsedUrl) {
  const port = parsedUrl.port || (parsedUrl.protocol === 'https:' ? '443' : '80');
  return `${parsedUrl.protocol}//${normalizeHostname(parsedUrl.hostname)}:${port}`;
}

const url = new URL(VOCECHAT_URL);
const urlHostname = normalizeHostname(url.hostname);

if (urlHostname === 'example.com' || urlHostname.endsWith('.example.com')) {
  console.error('❌ VOCECHAT_URL still points at the example.com placeholder.');
  process.exit(1);
}

const payload = JSON.stringify({
  content_type: "text/markdown",
  content: message
});

function sendRequest(targetUrl, method, body, redirectsRemaining) {
  // URL.hostname keeps the brackets on IPv6 literals, but net.connect expects
  // the bare address (e.g. "::1" rather than "[::1]").
  const hostname = targetUrl.hostname.startsWith('[')
    ? targetUrl.hostname.slice(1, -1)
    : targetUrl.hostname;

  const headers = {
    'x-api-key': API_KEY
  };
  if (body !== null) {
    headers['Content-Type'] = 'application/json';
    headers['Content-Length'] = Buffer.byteLength(body);
  }

  const options = {
    method,
    hostname,
    port: targetUrl.port || undefined,
    path: targetUrl.pathname + targetUrl.search,
    headers
  };

  const transport = targetUrl.protocol === 'http:' ? http : https;

  const req = transport.request(options, (res) => {
    let settled = false;

    const fail = (message) => {
      if (settled) return;
      settled = true;
      console.error(message);
      process.exit(1);
    };

    res.on('data', () => {}); // drain
    res.on('end', () => {
      if (settled) return;
      if (!res.complete) {
        fail('❌ VoceChat response ended before it completed.');
        return;
      }

      const location = res.headers.location;
      if (REDIRECT_STATUSES.has(res.statusCode) && location) {
        if (redirectsRemaining === 0) {
          fail('❌ VoceChat redirect limit exceeded');
          return;
        }

        let nextUrl;
        try {
          nextUrl = new URL(location, targetUrl);
        } catch (err) {
          fail(`❌ Failed to follow VoceChat redirect: ${err.message}`);
          return;
        }

        // Never forward the API key to a different origin.
        if (origin(nextUrl) !== origin(targetUrl)) {
          fail(`❌ Refusing to follow VoceChat redirect to a different origin: ${nextUrl.href}`);
          return;
        }

        // 303 See Other (and legacy 301/302) is followed with a bodyless
        // GET; 307/308 repeat the current method and body.
        const followWithGet = res.statusCode === 301 ||
          res.statusCode === 302 ||
          res.statusCode === 303;
        settled = true;
        sendRequest(
          nextUrl,
          followWithGet ? 'GET' : method,
          followWithGet ? null : body,
          redirectsRemaining - 1
        );
        return;
      }

      settled = true;
      if (res.statusCode >= 200 && res.statusCode < 300) {
        console.log(`✅ VoceChat responded ${res.statusCode}`);
      } else {
        console.error(`❌ VoceChat responded ${res.statusCode}`);
        process.exit(1);
      }
    });
    res.on('error', (err) => {
      fail(`❌ Failed to read VoceChat response: ${err.message}`);
    });
    res.on('aborted', () => {
      fail('❌ VoceChat response was aborted before it completed.');
    });
    res.on('close', () => {
      if (!res.complete) {
        fail('❌ VoceChat response closed before it completed.');
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

  if (body !== null) {
    req.write(body);
  }
  req.end();
}

sendRequest(url, 'POST', payload, MAX_REDIRECTS);