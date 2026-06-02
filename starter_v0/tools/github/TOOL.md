---
name: github
track: team
kind: live_api
provider: GitHub API
requires_env: []
inputs: [query, repository, sort]
outputs: [items, total_results, data]
side_effect: false
---
# github

Searches GitHub repositories by query or retrieves detailed information for a specific repository.
Supports token-based authentication via `GITHUB_TOKEN` environment variable.
