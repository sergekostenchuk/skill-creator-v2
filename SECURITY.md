# Security Policy

## Secret Handling

Do not store API keys, npm tokens, OAuth credentials, cookies, private URLs, or local `.env` values in skills, evals, reports, package files, issues, or pull requests.

`skill-creator-v2` treats unknown or unsafe dependency installation as `manual_approval_required` or `hard_blocked`. It should not auto-approve unpinned `latest` dependencies or packages without integrity evidence.

## Reporting

Please report security issues privately to the repository owner. Do not open a public issue containing secrets or exploit details.
