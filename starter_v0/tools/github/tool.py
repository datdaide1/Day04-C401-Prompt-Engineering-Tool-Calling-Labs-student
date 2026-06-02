from __future__ import annotations

import os
from typing import Any
import requests

from tools._shared import TIMEOUT, err


def search_github(query: str = "", repository: str = "", sort: str = "stars") -> dict[str, Any]:
    """Search GitHub repositories or fetch repository details.

    Args:
        query: Search query string (e.g. 'llama-3'). Used if repository is not specified.
        repository: Full repo name (e.g. 'facebookresearch/llama'). If specified, retrieves repo details.
        sort: Field to sort search results by ('stars', 'forks', or 'updated'). Default is 'stars'.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI20k-Research-Agent/1.0",
    }
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        if repository:
            # Get repository details
            repo_url = f"https://api.github.com/repos/{repository}"
            response = requests.get(repo_url, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            repo_data = response.json()
            
            return {
                "tool": "github",
                "mode": "details",
                "repository": repository,
                "data": {
                    "name": repo_data.get("name"),
                    "full_name": repo_data.get("full_name"),
                    "description": repo_data.get("description"),
                    "html_url": repo_data.get("html_url"),
                    "stars": repo_data.get("stargazers_count"),
                    "forks": repo_data.get("forks_count"),
                    "watchers": repo_data.get("watchers_count"),
                    "language": repo_data.get("language"),
                    "open_issues": repo_data.get("open_issues_count"),
                    "created_at": repo_data.get("created_at"),
                    "updated_at": repo_data.get("updated_at"),
                }
            }
        
        elif query:
            # Search repositories
            search_url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": sort,
                "order": "desc",
                "per_page": 5
            }
            response = requests.get(search_url, headers=headers, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            search_data = response.json()
            
            items = []
            for item in search_data.get("items", []):
                items.append({
                    "name": item.get("name"),
                    "full_name": item.get("full_name"),
                    "description": item.get("description"),
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count"),
                    "forks": item.get("forks_count"),
                    "language": item.get("language"),
                })
            
            return {
                "tool": "github",
                "mode": "search",
                "query": query,
                "total_results": search_data.get("total_count", 0),
                "items": items
            }
        
        else:
            return {
                "tool": "github",
                "error": "Either query or repository parameter must be provided."
            }

    except Exception as exc:
        return err("github", exc)
