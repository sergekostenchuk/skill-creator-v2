Expected result:

- `requests@latest-stable` is not auto-approved as production-safe.
- `@browserbasehq/mcp-server-browserbase@2.4.2` is hard-blocked if present in blocklist.
- `firecrawl-mcp@9.99.9` requires manual approval because of version drift from any pinned allowlist entry.
- The output reports install decisions and does not install anything during planning.
