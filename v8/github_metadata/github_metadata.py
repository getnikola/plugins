# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (c) 2026 Stephane Manet
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import json
import os
import re
import ssl
import time
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
from urllib.error import URLError
from urllib.request import Request, urlopen

from blinker import signal
from nikola.plugin_categories import SignalHandler # type: ignore

try:
    import certifi
except ImportError:
    certifi = None


# ----------------------------
# Settings
# ----------------------------

@dataclass(frozen=True)
class PublicReposSettings:
    enabled: bool = True
    user: Optional[str] = None          # GitHub login (user)
    sort: str = "pushed"                # created, updated, pushed, full_name
    direction: str = "desc"             # asc, desc
    include_forks: bool = False
    include_archived: bool = False
    limit: int = 200                    # safety limit


@dataclass(frozen=True)
class Settings:
    enabled: bool = True
    inject_as: str = "github"
    api_url: str = "https://api.github.com"
    cache_ttl: int = 3600               # seconds

    # Optional: for parity (single repo metadata)
    repository: Optional[str] = None    # "owner/repo" (optional)

    public_repositories: PublicReposSettings = PublicReposSettings()
    manual_repositories: Optional[List[Dict[str, Any]]] = None


# ----------------------------
# Plugin
# ----------------------------

class GithubMetadata(SignalHandler):
    """Inject GitHub metadata into GLOBAL_CONTEXT for templates."""

    name = "github_metadata"

    def set_site(self, site):
        super().set_site(site)
        signal("configured").connect(self._on_configured, sender=site)

    def _on_configured(self, site):
        raw_cfg = site.config.get("GITHUB_METADATA") or {}
        s = _parse_settings(raw_cfg)

        if not s.enabled:
            self.logger.info("github_metadata: disabled.")
            return

        cache_dir = _cache_dir(site)

        # Determine repo (optional) and user (for public repos)
        detected_repo_nwo = _detect_repo_nwo(site)
        repo_nwo = s.repository
        owner_source = repo_nwo or detected_repo_nwo
        detected_owner = owner_source.split("/", 1)[0] if owner_source and "/" in owner_source else None
        manual_repos = _normalize_manual_repos(s.manual_repositories, s.public_repositories.user)
        manual_owner = _detect_owner_from_repos(manual_repos)

        user_login = s.public_repositories.user or manual_owner or detected_owner or os.environ.get("GITHUB_ACTOR")
        if not user_login and not manual_repos:
            self.logger.warning(
                "github_metadata: cannot determine GitHub user. "
                "Set GITHUB_METADATA['public_repositories']['user']."
            )
            return
        if not user_login:
            user_login = "manual"

        if raw_cfg.get("token"):
            self.logger.warning(
                "github_metadata: token is ignored; this plugin uses only unauthenticated requests."
            )

        client = _GitHubClient(api_url=s.api_url, logger=self.logger)

        github_obj: Dict[str, Any] = {
            "api_url": s.api_url,
            "user_login": user_login,
            "repository_nwo": repo_nwo,
            "public_repositories": [],
            "repository": None,
            "errors": [],
            "generated_at": int(time.time()),
        }

        # 1) Fetch public repositories (main goal)
        if manual_repos:
            github_obj["public_repositories"] = manual_repos
        elif s.public_repositories.enabled:
            cache_key = _public_repos_cache_key(user_login, s.public_repositories)
            cache_path = os.path.join(cache_dir, cache_key)

            repos = _read_cache_json(cache_path, ttl=s.cache_ttl)
            if repos is None:
                try:
                    repos = client.list_user_public_repos(
                        user=user_login,
                        sort=s.public_repositories.sort,
                        direction=s.public_repositories.direction,
                        limit=s.public_repositories.limit,
                    )
                    repos = _filter_repos(
                        repos,
                        include_forks=s.public_repositories.include_forks,
                        include_archived=s.public_repositories.include_archived,
                    )
                    _write_cache_json(cache_path, repos)
                except Exception as e:
                    github_obj["errors"].append(f"public_repositories: {e!r}")
                    # fallback to stale cache if present
                    repos = _read_cache_json_any(cache_path) or []

            github_obj["public_repositories"] = repos

        # 2) Optional: single repo metadata (nice-to-have parity)
        if repo_nwo:
            cache_path = os.path.join(cache_dir, _repo_cache_key(repo_nwo))
            repo_obj = _read_cache_json(cache_path, ttl=s.cache_ttl)
            if repo_obj is None:
                try:
                    repo_obj = client.get_repo(repo_nwo)
                    _write_cache_json(cache_path, repo_obj)
                except Exception as e:
                    github_obj["errors"].append(f"repository: {e!r}")
                    repo_obj = _read_cache_json_any(cache_path)

            github_obj["repository"] = repo_obj

        # Inject into GLOBAL_CONTEXT (templates)
        gc = site.config.setdefault("GLOBAL_CONTEXT", {})
        gc[s.inject_as] = github_obj

        # Some Nikola versions keep a copy — harmless best-effort:
        for attr in ("GLOBAL_CONTEXT", "_GLOBAL_CONTEXT"):
            try:
                obj = getattr(site, attr)
                if isinstance(obj, dict):
                    obj[s.inject_as] = github_obj
            except Exception:
                pass

        self.logger.info(
            f"github_metadata: injected '{s.inject_as}' (user={user_login}, "
            f"repos={len(github_obj['public_repositories'])})."
        )
        if github_obj["errors"]:
            self.logger.warning(
                "github_metadata: errors: %s", "; ".join(github_obj["errors"])
            )


# ----------------------------
# Settings parsing
# ----------------------------

def _parse_settings(cfg: Dict[str, Any]) -> Settings:
    pr_cfg = (cfg.get("public_repositories") or {})
    pr = PublicReposSettings(
        enabled=bool(pr_cfg.get("enabled", True)),
        user=pr_cfg.get("user"),
        sort=pr_cfg.get("sort", "pushed"),
        direction=pr_cfg.get("direction", "desc"),
        include_forks=bool(pr_cfg.get("include_forks", False)),
        include_archived=bool(pr_cfg.get("include_archived", False)),
        limit=int(pr_cfg.get("limit", 200)),
    )
    manual_repositories = cfg.get("manual_repositories") or None

    return Settings(
        enabled=bool(cfg.get("enabled", True)),
        inject_as=cfg.get("inject_as", "github"),
        api_url=cfg.get("api_url", "https://api.github.com"),
        cache_ttl=int(cfg.get("cache_ttl", 3600)),
        repository=cfg.get("repository"),
        public_repositories=pr,
        manual_repositories=manual_repositories,
    )



# ----------------------------
# GitHub client (urllib, no requests)
# ----------------------------

class _GitHubClient:
    def __init__(self, api_url: str, logger):
        self.api_url = api_url.rstrip("/")
        self.logger = logger

    def get_repo(self, repo_nwo: str) -> Dict[str, Any]:
        owner, repo = repo_nwo.split("/", 1)
        return self._get_json(f"/repos/{owner}/{repo}")[0]

    def list_user_public_repos(
        self,
        user: str,
        sort: str = "pushed",
        direction: str = "desc",
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        # GitHub API: GET /users/{username}/repos?type=public&per_page=100&sort=...&direction=...
        path = f"/users/{user}/repos?type=public&per_page=100&sort={sort}&direction={direction}"
        items: List[Dict[str, Any]] = []
        next_url: Optional[str] = self.api_url + path

        while next_url and len(items) < limit:
            data, headers = self._get_json_abs(next_url)
            if isinstance(data, list):
                items.extend(data)
            else:
                break

            next_url = _parse_next_link(headers.get("Link"))
        return items[:limit]

    def _get_json(self, path: str) -> Tuple[Any, Dict[str, str]]:
        return self._get_json_abs(self.api_url + path)

    def _get_json_abs(self, url: str) -> Tuple[Any, Dict[str, str]]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "nikola-github-metadata/0.2.0",
        }

        req = Request(url, headers=headers, method="GET")
        context = None
        if certifi is not None:
            context = ssl.create_default_context(cafile=certifi.where())
        try:
            with urlopen(req, timeout=20, context=context) as resp:
                raw = resp.read().decode("utf-8", errors="replace")

                if resp.status == 403 and "rate limit" in raw.lower():
                    raise RuntimeError("GitHub API rate limit exceeded (unauthenticated)")

                if resp.status >= 400:
                    raise RuntimeError(f"GET {url} -> {resp.status}: {raw[:200]}")

                data = json.loads(raw)
                hdrs = {k: v for (k, v) in resp.headers.items()}
                return data, hdrs
        except URLError as exc:
            reason = getattr(exc, "reason", None)
            if isinstance(reason, ssl.SSLCertVerificationError):
                raise RuntimeError(
                    "SSL certificate verification failed. On macOS, run the "
                    "Python 'Install Certificates.command' or install certifi."
                ) from exc
            raise



def _parse_next_link(link_header: Optional[str]) -> Optional[str]:
    # Link: <...>; rel="next", <...>; rel="last"
    if not link_header:
        return None
    for part in link_header.split(","):
        part = part.strip()
        if 'rel="next"' in part:
            m = re.search(r"<([^>]+)>", part)
            if m:
                return m.group(1)
    return None


# ----------------------------
# Repo detection (optional)
# ----------------------------

def _detect_repo_nwo(site) -> Optional[str]:
    env = os.environ.get("GITHUB_REPOSITORY")
    if env and "/" in env:
        return env.strip()

    base = site.config.get("BASE_FOLDER") or os.getcwd()
    try:
        remote = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=base,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return None

    return _parse_repo_from_remote(remote)


def _parse_repo_from_remote(remote: str) -> Optional[str]:
    remote = remote.strip()

    m = re.match(r"git@[^:]+:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", remote)
    if m:
        return f"{m.group('owner')}/{m.group('repo')}"

    if remote.startswith(("http://", "https://", "ssh://")):
        u = urlparse(remote)
        path = (u.path or "").lstrip("/")
        if path.endswith(".git"):
            path = path[:-4]
        if path.count("/") >= 1:
            owner, repo = path.split("/", 1)
            return f"{owner}/{repo}"

    return None


# ----------------------------
# Filtering + caching
# ----------------------------

def _filter_repos(
    repos: List[Dict[str, Any]],
    include_forks: bool,
    include_archived: bool,
) -> List[Dict[str, Any]]:
    out = []
    for r in repos:
        if (not include_forks) and r.get("fork"):
            continue
        if (not include_archived) and r.get("archived"):
            continue
        out.append(r)
    return out


def _normalize_manual_repos(
    repos: Optional[List[Any]],
    default_owner: Optional[str],
) -> List[Dict[str, Any]]:
    if not repos:
        return []
    out: List[Dict[str, Any]] = []
    for item in repos:
        if isinstance(item, str):
            name = item.strip()
            if not name:
                continue
            if "/" in name:
                owner, repo_name = name.split("/", 1)
            else:
                owner, repo_name = default_owner, name
            repo: Dict[str, Any] = {"name": repo_name}
            if owner:
                full_name = f"{owner}/{repo_name}"
                repo["full_name"] = full_name
                repo["html_url"] = f"https://github.com/{full_name}"
            else:
                repo["full_name"] = name
            out.append(repo)
            continue

        if isinstance(item, dict):
            repo = dict(item)
            full_name = repo.get("full_name")
            name = repo.get("name")
            if not name and full_name and "/" in full_name:
                repo["name"] = full_name.split("/", 1)[1]
                name = repo["name"]
            if not full_name and name and default_owner:
                repo["full_name"] = f"{default_owner}/{name}"
                full_name = repo["full_name"]
            if "html_url" not in repo and full_name and "/" in full_name:
                repo["html_url"] = f"https://github.com/{full_name}"
            out.append(repo)

    return out


def _detect_owner_from_repos(repos: List[Dict[str, Any]]) -> Optional[str]:
    for repo in repos:
        full_name = repo.get("full_name")
        if full_name and "/" in full_name:
            return full_name.split("/", 1)[0]
    return None


def _cache_dir(site) -> str:
    d = site.config.get("CACHE_FOLDER")
    if not d:
        base = site.config.get("BASE_FOLDER") or "."
        d = os.path.join(base, "cache")
    os.makedirs(d, exist_ok=True)
    return d


def _public_repos_cache_key(user: str, pr: PublicReposSettings) -> str:
    # include sort/direction + filters in filename to avoid mixing caches
    safe_user = user.replace("/", "_")
    return (
        f"github_metadata__public_repos__{safe_user}"
        f"__sort-{pr.sort}__dir-{pr.direction}"
        f"__forks-{int(pr.include_forks)}__arch-{int(pr.include_archived)}.json"
    )


def _repo_cache_key(repo_nwo: str) -> str:
    safe = repo_nwo.replace("/", "__")
    return f"github_metadata__repo__{safe}.json"


def _read_cache_json(path: str, ttl: int) -> Optional[Any]:
    try:
        st = os.stat(path)
        if (time.time() - st.st_mtime) <= ttl:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None
    return None


def _read_cache_json_any(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_cache_json(path: str, data: Any) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, path)
