#!/usr/bin/env python3
"""
aspace_plugin_registry_organ.py — Organe Natif du Registre de Plugins (CORPS / Organe K2).

Porte 1:1 sans perte le cœur fonctionnel, les bornes de validation, la compilation d'index,
le protocole atomique de publication/récupération sur Releases et l'audit d'hygiène Agent Zero
de `M001` (`a0-plugins`, pin `fa8df85`), raccordé au bus L0 (`fondation-13-1` /
`aspace_foundation_kernel.py`), sans dépendance réseau par défaut ni auto-certification.
"""

from __future__ import annotations

import base64
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, NoReturn, Optional, Sequence, Set, Tuple, cast

import yaml
from PIL import Image

_CORE_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = _CORE_DIR.parents[2]
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from aspace_foundation_kernel import (  # noqa: E402
    ContractViolation,
    consign_measured_l0_evidence,
)

# ===========================================================================
# Constantes & Exceptions (M001 a0-plugins)
# ===========================================================================

DEFAULT_MAX_PLUGINS = 1000
INDEX_YAML_NAME = "index.yaml"
PLUGIN_DIRNAME_PATTERN = re.compile(r"^[a-z0-9_]+$")

ALLOWED_FIELDS = {"title", "description", "github", "tags", "screenshots"}
REQUIRED_FIELDS = {"title", "description", "github"}
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_IMAGE_EXTS_ORDER = (".png", ".jpg", ".jpeg", ".webp")
THUMBNAIL_MAX_BYTES = 20 * 1024
SCREENSHOT_MAX_BYTES = 2 * 1024 * 1024
INDEX_YAML_MAX_CHARS = 2000
TITLE_MAX_LEN = 50
DESCRIPTION_MAX_LEN = 500
MAX_TAGS = 5
MAX_SCREENSHOTS = 5

DISCUSSIONS_CATEGORY_NAME = "Plugins"
DISCUSSION_MARKER = "<!-- a0-plugins-discussion -->"
PLUGIN_MARKER_PREFIX = "<!-- a0-plugins-plugin:"
PLUGIN_MARKER_RE = re.compile(r"<!-- a0-plugins-plugin:([^>]+?) -->")
SUSPENDED_MD_NAME = "suspended.md"
BLOCKED_MD_NAME = "blocked.md"

DEFAULT_RELEASE_TAG = "generated-index"
DEFAULT_RELEASE_NAME = "Generated Index"
DEFAULT_ASSET_NAME = "index.json"
DEFAULT_CHUNK_SIZE = 50

ABANDONED_AGENT_ZERO = ("_plugin_installer", "_plugin_scan", "_plugin_validator")
SURFACES_AGENT_ZERO = (
    "_telegram_integration",
    "_whatsapp_integration",
    "_email_integration",
    "_kokoro_tts",
    "_whisper_stt",
    "_office",
    "_oauth",
    "_pin_to_top",
    "_sidebar_folders",
)
REQUIRED_INDEX_KEYS = ("title", "description", "github")


class PluginResolutionError(Exception):
    pass


class ValidatePluginSubmissionError(Exception):
    pass


class SyncPluginStateError(Exception):
    pass


class GitHubHttpError(SyncPluginStateError):
    def __init__(
        self,
        *,
        status: int,
        method: str,
        url: str,
        request_id: str,
        scopes: str,
        body: str,
    ) -> None:
        super().__init__(f"HTTP {status} {method} {url}")
        self.status = status
        self.method = method
        self.url = url
        self.request_id = request_id
        self.scopes = scopes
        self.body = body


class FindOrphanPluginNamesError(Exception):
    pass


class UpdateStarsError(Exception):
    pass


class PublishReleaseError(Exception):
    pass


class DownloadIndexError(Exception):
    pass


# ===========================================================================
# 1. Résolution & sélection des plugins (scripts/plugin_resolution.py)
# ===========================================================================


def is_valid_plugin_dirname(plugin_name: str) -> bool:
    return bool(PLUGIN_DIRNAME_PATTERN.fullmatch(plugin_name))


def is_reserved_plugin_dirname(plugin_name: str) -> bool:
    return plugin_name.startswith("_")


def is_zero_sha(sha: Optional[str]) -> bool:
    if not sha:
        return True
    s = sha.strip()
    return bool(s) and set(s) == {"0"}


def normalize_plugin_names(names: Sequence[str], *, allow_reserved: bool = False) -> List[str]:
    filtered: List[str] = []
    for n in names:
        if n and is_valid_plugin_dirname(n) and (allow_reserved or not is_reserved_plugin_dirname(n)):
            filtered.append(n)
    return sorted(set(filtered))


def resolve_plugin_names(
    *,
    all_paths: Optional[Sequence[str]] = None,
    diff_paths: Optional[Sequence[str]] = None,
    plugin_names_env: str = "",
    before_sha: str = "",
    after_sha: str = "",
    start_from: str = "",
    max_plugins: int = DEFAULT_MAX_PLUGINS,
) -> List[str]:
    """Port 1:1 de `get_plugin_names()` sans dépendre de subprocess git obligatoire."""
    env_names = plugin_names_env.strip()
    if env_names:
        raw_names = [n.strip() for n in env_names.split(",") if n.strip()]
        plugin_names = normalize_plugin_names(raw_names, allow_reserved=True)
    else:
        before = before_sha.strip()
        _ = after_sha.strip()
        if not before or is_zero_sha(before):
            paths = list(all_paths or [])
        else:
            paths = list(diff_paths or [])
        plugin_names_set: Set[str] = set()
        for p in paths:
            parts = Path(p).parts
            if len(parts) >= 2 and parts[0] == "plugins":
                plugin_names_set.add(parts[1])
        plugin_names = normalize_plugin_names(list(plugin_names_set))

    if not plugin_names:
        return []

    start_str = start_from.strip()
    if start_str:
        try:
            start_idx = int(start_str)
            if start_idx > 0:
                plugin_names = plugin_names[start_idx:]
        except ValueError:
            pass

    if len(plugin_names) > max_plugins:
        raise PluginResolutionError(
            f"Detected {len(plugin_names)} plugins in scope, which exceeds MAX_PLUGINS={max_plugins}. "
            "Increase MAX_PLUGINS or run multiple smaller pushes."
        )
    return plugin_names


# ===========================================================================
# 2. Validation des soumissions & bornes strictes (validate_plugin_submission.py)
# ===========================================================================


def _fail_val(msg: str) -> NoReturn:
    raise ValidatePluginSubmissionError(msg)


def validate_plugin_name_format(plugin_name: str, *, context: str) -> None:
    if is_valid_plugin_dirname(plugin_name):
        return
    _fail_val(
        f"{context} '{plugin_name}' is invalid: "
        "expected lowercase letters, numbers, and underscores only "
        "(dashes are not allowed)"
    )


def submission_plugin_name(paths: Sequence[str]) -> str:
    plugin_names: Set[str] = set()
    for path in paths:
        parts = Path(path).parts
        if not parts:
            continue
        if parts[0] != "plugins":
            _fail_val(f"Only files under plugins/ are allowed in plugin PRs: {path}")
        if len(parts) < 2:
            _fail_val(f"Invalid plugin path: {path}")
        plugin_name = parts[1]
        if not plugin_name or plugin_name.startswith("_"):
            _fail_val(f"Plugin folder names starting with '_' are reserved: {path}")
        validate_plugin_name_format(plugin_name, context="Plugin folder name")
        plugin_names.add(plugin_name)
    if len(plugin_names) != 1:
        _fail_val("PR must modify exactly one plugin folder under plugins/")
    return next(iter(plugin_names))


def is_deletion_pr(entries: Sequence[Tuple[str, Sequence[str]]], plugin_name: str) -> bool:
    if not entries:
        return False
    for status, paths in entries:
        if not status.startswith("D"):
            return False
        for path in paths:
            parts = Path(path).parts
            if len(parts) < 2 or parts[0] != "plugins" or parts[1] != plugin_name:
                return False
    return True


def parse_repo_url(url: str) -> Optional[Tuple[str, str]]:
    match = re.match(r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url.strip())
    if not match:
        return None
    return match.group(1), match.group(2)


def normalize_repo_url(url: str) -> Optional[str]:
    parsed = parse_repo_url(url)
    if not parsed:
        return None
    owner, repo = parsed
    return f"https://github.com/{owner.lower()}/{repo.lower()}"


def repo_owner_from_url(url: str) -> Optional[str]:
    parsed = parse_repo_url(url)
    if not parsed:
        return None
    owner, _ = parsed
    return owner


def read_plugin_yaml_text_strict(raw_text: str, *, rel_path: str = INDEX_YAML_NAME) -> Dict[str, Any]:
    if len(raw_text) > INDEX_YAML_MAX_CHARS:
        _fail_val(f"{INDEX_YAML_NAME} exceeds max total length {INDEX_YAML_MAX_CHARS} characters")
    try:
        loaded = yaml.safe_load(raw_text)
    except Exception as e:
        _fail_val(f"Invalid YAML in {rel_path}: {e}")
    if not isinstance(loaded, dict):
        _fail_val(f"{INDEX_YAML_NAME} must be a YAML mapping/object")
    return cast(Dict[str, Any], loaded)


def validate_github_repo_not_in_index(
    plugin_name: str, url: str, index_plugins: Dict[str, Any]
) -> None:
    normalized_url = normalize_repo_url(url)
    if not normalized_url:
        return
    for indexed_plugin_name, indexed_plugin in index_plugins.items():
        if indexed_plugin_name == plugin_name or not isinstance(indexed_plugin, dict):
            continue
        indexed_url = indexed_plugin.get("github")
        if not isinstance(indexed_url, str):
            continue
        if normalize_repo_url(indexed_url) == normalized_url:
            _fail_val(
                f"github repository is already present in index.json for plugin '{indexed_plugin_name}'"
            )


def validate_remote_plugin_name(content_obj: Dict[str, Any], plugin_name: str) -> None:
    if content_obj.get("encoding") != "base64" or not isinstance(content_obj.get("content"), str):
        _fail_val("unable to read remote plugin.yaml contents")
    try:
        encoded_content = cast(str, content_obj.get("content"))
        decoded_bytes = base64.b64decode(encoded_content, validate=False)
        decoded_text = decoded_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        _fail_val(f"unable to decode remote plugin.yaml contents: {e}")
    try:
        remote_yaml = yaml.safe_load(decoded_text)
    except Exception as e:
        _fail_val(f"remote plugin.yaml is invalid YAML: {e}")
    if not isinstance(remote_yaml, dict):
        _fail_val("remote plugin.yaml must be a YAML mapping/object")
    remote_name = remote_yaml.get("name")
    if not isinstance(remote_name, str) or not remote_name.strip():
        _fail_val("remote plugin.yaml must contain non-empty string field 'name'")
    validate_plugin_name_format(remote_name, context="remote plugin.yaml name")
    if remote_name != plugin_name:
        _fail_val(f"remote plugin.yaml name must exactly match plugin folder name '{plugin_name}'")


def validate_github_repo(
    url: str,
    plugin_name: str,
    *,
    request_json_fn: Callable[[str], Dict[str, Any]],
) -> None:
    parsed = parse_repo_url(url)
    if not parsed:
        _fail_val("github must be a valid GitHub repository URL")
    owner, repo = parsed
    repo_obj = request_json_fn(f"https://api.github.com/repos/{owner}/{repo}")
    if not isinstance(repo_obj.get("full_name"), str):
        _fail_val("github repository does not exist or is inaccessible")
    content_obj = request_json_fn(f"https://api.github.com/repos/{owner}/{repo}/contents/plugin.yaml")
    if content_obj.get("type") != "file":
        _fail_val("github repository must contain plugin.yaml at repository root")
    validate_remote_plugin_name(content_obj, plugin_name)


def validate_screenshot_url(
    url: str,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> None:
    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        _fail_val("screenshots entries must be full http/https URLs")
    suffix = Path(parsed.path).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTS:
        _fail_val("screenshots URLs must end with png/jpg/jpeg/webp")

    req = urllib.request.Request(
        url.strip(),
        method="HEAD",
        headers={"User-Agent": "a0-plugins-validate-plugin-submission"},
    )
    try:
        with opener(req, timeout=30) as resp:
            content_length = resp.headers.get("Content-Length", "").strip()
            if content_length:
                try:
                    if int(content_length) > SCREENSHOT_MAX_BYTES:
                        _fail_val("screenshot exceeds 2 MB")
                except ValueError:
                    pass
            return
    except urllib.error.HTTPError as e:
        if e.code not in {405, 501}:
            msg = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
            _fail_val(f"screenshot URL is not reachable ({e.code}): {msg}")
    except Exception as e:
        _fail_val(f"screenshot URL is not reachable: {e}")

    req = urllib.request.Request(
        url.strip(),
        method="GET",
        headers={
            "User-Agent": "a0-plugins-validate-plugin-submission",
            "Range": f"bytes=0-{SCREENSHOT_MAX_BYTES}",
        },
    )
    try:
        with opener(req, timeout=30) as resp:
            data = resp.read(SCREENSHOT_MAX_BYTES + 1)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        _fail_val(f"screenshot URL is not reachable ({e.code}): {msg}")
    except Exception as e:
        _fail_val(f"screenshot URL is not reachable: {e}")
    if len(data) > SCREENSHOT_MAX_BYTES:
        _fail_val("screenshot exceeds 2 MB")


def validate_screenshot_urls(
    screenshots: Any,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> None:
    if not isinstance(screenshots, list):
        _fail_val("screenshots must be a list of full image URLs")
    if len(screenshots) > MAX_SCREENSHOTS:
        _fail_val(f"screenshots must contain at most {MAX_SCREENSHOTS} items")
    for screenshot in screenshots:
        if not isinstance(screenshot, str) or not screenshot.strip():
            _fail_val("screenshots must be a list of non-empty strings")
        validate_screenshot_url(screenshot, opener=opener)


def validate_fields(
    meta: Dict[str, Any],
    plugin_name: str,
    *,
    request_json_fn: Optional[Callable[[str], Dict[str, Any]]] = None,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> None:
    keys = set(meta.keys())
    unknown = sorted(k for k in keys if k not in ALLOWED_FIELDS)
    if unknown:
        _fail_val(f"{INDEX_YAML_NAME} contains unsupported fields: {', '.join(unknown)}")
    missing = sorted(
        k for k in REQUIRED_FIELDS if not isinstance(meta.get(k), str) or not cast(str, meta.get(k)).strip()
    )
    if missing:
        _fail_val(f"{INDEX_YAML_NAME} is missing required non-empty fields: {', '.join(missing)}")

    title = cast(str, meta.get("title"))
    description = cast(str, meta.get("description"))
    github = cast(str, meta.get("github"))
    if len(title.strip()) > TITLE_MAX_LEN:
        _fail_val(f"title exceeds max length {TITLE_MAX_LEN}")
    if len(description.strip()) > DESCRIPTION_MAX_LEN:
        _fail_val(f"description exceeds max length {DESCRIPTION_MAX_LEN}")
    if request_json_fn is not None:
        validate_github_repo(github, plugin_name, request_json_fn=request_json_fn)
    elif not parse_repo_url(github):
        _fail_val("github must be a valid GitHub repository URL")

    tags = meta.get("tags")
    if tags is not None:
        if not isinstance(tags, list) or not all(isinstance(t, str) and t.strip() for t in tags):
            _fail_val("tags must be a list of non-empty strings")
        if len(tags) > MAX_TAGS:
            _fail_val(f"tags must contain at most {MAX_TAGS} items")

    screenshots = meta.get("screenshots")
    if screenshots is not None:
        validate_screenshot_urls(screenshots, opener=opener)


def validate_thumbnail(plugin_dir: Path) -> None:
    plugin_files = sorted(p.name for p in plugin_dir.iterdir() if p.is_file()) if plugin_dir.is_dir() else []
    thumbnails = [name for name in plugin_files if Path(name).stem == "thumbnail"]
    if len(thumbnails) > 1:
        _fail_val("Only one thumbnail file is allowed")
    if not thumbnails:
        return
    thumbnail_name = thumbnails[0]
    thumbnail = Path(thumbnail_name)
    if thumbnail.suffix.lower() not in ALLOWED_IMAGE_EXTS:
        _fail_val("thumbnail must be png/jpg/jpeg/webp")
    thumbnail_bytes = (plugin_dir / thumbnail_name).read_bytes()
    if len(thumbnail_bytes) > THUMBNAIL_MAX_BYTES:
        _fail_val("thumbnail exceeds 20 KB")
    with Image.open(io.BytesIO(thumbnail_bytes)) as img:
        width, height = img.size
    if width != height:
        _fail_val("thumbnail must be square")


def validate_allowed_files(plugin_dir: Path) -> None:
    if not plugin_dir.is_dir():
        return
    for item in sorted(plugin_dir.iterdir()):
        name = item.name
        path = Path(name)
        if path.name == INDEX_YAML_NAME:
            continue
        if path.stem == "thumbnail" and path.suffix.lower() in ALLOWED_IMAGE_EXTS:
            continue
        _fail_val(f"Unexpected file in plugin folder: {path.name}")


# ===========================================================================
# 3. Compilation d'état & indexation (scripts/sync_plugin_state.py)
# ===========================================================================


def _fail_sync(msg: str) -> NoReturn:
    raise SyncPluginStateError(msg)


def plugin_exists(plugins_dir: Path, plugin_name: str) -> bool:
    if is_reserved_plugin_dirname(plugin_name):
        return False
    plugin_dir = plugins_dir / plugin_name
    return (plugin_dir / INDEX_YAML_NAME).exists() and not (plugin_dir / BLOCKED_MD_NAME).exists()


def plugin_blocked(plugins_dir: Path, plugin_name: str) -> bool:
    plugin_dir = plugins_dir / plugin_name
    return plugin_dir.exists() and (plugin_dir / BLOCKED_MD_NAME).exists()


def plugin_suspended_markdown(plugins_dir: Path, plugin_name: str) -> Optional[str]:
    suspended_md = plugins_dir / plugin_name / SUSPENDED_MD_NAME
    if not suspended_md.exists():
        return None
    return suspended_md.read_text(encoding="utf-8").strip() or None


def read_plugin_yaml(plugins_dir: Path, plugin_name: str) -> Dict[str, Any]:
    plugin_yaml = plugins_dir / plugin_name / INDEX_YAML_NAME
    if not plugin_yaml.exists():
        _fail_sync(f"Missing {INDEX_YAML_NAME} for plugin '{plugin_name}': {plugin_yaml}")
    try:
        loaded = yaml.safe_load(plugin_yaml.read_text(encoding="utf-8"))
    except Exception as e:
        _fail_sync(f"Invalid YAML for plugin '{plugin_name}': {e}")
    if not isinstance(loaded, dict):
        _fail_sync(f"{INDEX_YAML_NAME} for '{plugin_name}' must be a YAML mapping/object")
    return cast(Dict[str, Any], loaded)


def read_authors(authors_dir: Path) -> Dict[str, Any]:
    if not authors_dir.exists() or not authors_dir.is_dir():
        return {}
    authors: Dict[str, Any] = {}
    for author_dir in sorted(authors_dir.iterdir(), key=lambda x: x.name):
        if not author_dir.is_dir():
            continue
        author_yaml = author_dir / "author.yaml"
        if not author_yaml.exists():
            continue
        try:
            loaded = yaml.safe_load(author_yaml.read_text(encoding="utf-8"))
        except Exception as e:
            _fail_sync(f"Invalid author metadata in {author_yaml}: {e}")
        if not isinstance(loaded, dict):
            _fail_sync(f"{author_yaml} must contain a YAML mapping/object")
        authors[author_dir.name] = loaded
    return authors


def repo_file_url(rel_path: str, *, owner: str, repo: str, ref: str = "main") -> str:
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref or 'main'}/{rel_path.lstrip('/')}"


def thumbnail_rel_path(repo_root: Path, plugin_name: str) -> Optional[str]:
    plugin_dir = repo_root / "plugins" / plugin_name
    if not plugin_dir.exists():
        return None
    for ext in ALLOWED_IMAGE_EXTS_ORDER:
        p = plugin_dir / f"thumbnail{ext}"
        if p.exists():
            return p.relative_to(repo_root).as_posix()
    generated_thumbnail = repo_root / "generated" / "thumbnails" / plugin_name / "thumbnail.jpg"
    if generated_thumbnail.exists():
        return generated_thumbnail.relative_to(repo_root).as_posix()
    return None


def parse_github_owner_from_url(url: str) -> Optional[str]:
    s = url.strip()
    if not s:
        return None
    s = s.removeprefix("https://").removeprefix("http://")
    if s.startswith("github.com/"):
        s = s[len("github.com/") :]
    if s.startswith("www.github.com/"):
        s = s[len("www.github.com/") :]
    if s.startswith("git@github.com:"):
        s = s[len("git@github.com:") :]
    s = s.strip("/")
    if s.endswith(".git"):
        s = s[: -len(".git")]
    parts = [p for p in s.split("/") if p]
    if len(parts) >= 2:
        return parts[0] or None
    return None


def index_plugin_entry(
    plugin_name: str,
    meta: Dict[str, Any],
    discussion_url: str,
    *,
    repo_root: Path,
    owner: str,
    repo: str,
    ref: str = "main",
) -> Dict[str, Any]:
    title = meta.get("title") if isinstance(meta.get("title"), str) else None
    description = meta.get("description") if isinstance(meta.get("description"), str) else None
    gh = meta.get("github") if isinstance(meta.get("github"), str) else None
    gh_str = gh if isinstance(gh, str) else ""
    author = parse_github_owner_from_url(gh_str) if gh_str else None
    tags_val = meta.get("tags")
    tags = [t for t in tags_val if isinstance(t, str) and t.strip()] if isinstance(tags_val, list) else None
    screenshots_val = meta.get("screenshots")
    screenshots = (
        [s.strip() for s in screenshots_val if isinstance(s, str) and s.strip()]
        if isinstance(screenshots_val, list)
        else []
    )
    thumb_rel = thumbnail_rel_path(repo_root, plugin_name)
    entry: Dict[str, Any] = {
        "title": title,
        "description": description,
        "github": gh,
        "author": author,
        "tags": tags,
        "thumbnail": repo_file_url(thumb_rel, owner=owner, repo=repo, ref=ref) if isinstance(thumb_rel, str) else None,
        "screenshots": screenshots,
        "discussion": discussion_url,
    }
    suspended = plugin_suspended_markdown(repo_root / "plugins", plugin_name)
    if suspended:
        entry["suspended"] = suspended
    return entry


def upsert_index_plugin(index: Dict[str, Any], plugin_name: str, entry: Dict[str, Any]) -> None:
    plugins = index.get("plugins")
    if not isinstance(plugins, dict):
        plugins = {}
        index["plugins"] = plugins
    existing = plugins.get(plugin_name)
    if isinstance(existing, dict):
        if isinstance(existing.get("stars"), int) and not isinstance(entry.get("stars"), int):
            entry["stars"] = existing.get("stars")
        if isinstance(existing.get("version"), str) and not isinstance(entry.get("version"), str):
            entry["version"] = existing.get("version")
        existing_commit = existing.get("commit")
        if isinstance(existing_commit, str) and existing_commit and not isinstance(entry.get("commit"), str):
            entry["commit"] = existing_commit
        existing_updated = existing.get("updated")
        if isinstance(existing_updated, str) and existing_updated and not isinstance(entry.get("updated"), str):
            entry["updated"] = existing_updated
    plugins[plugin_name] = entry


def remove_index_plugin(index: Dict[str, Any], plugin_name: str) -> bool:
    plugins = index.get("plugins")
    if not isinstance(plugins, dict) or plugin_name not in plugins:
        return False
    del plugins[plugin_name]
    return True


def render_discussion_body(
    plugin_name: str,
    meta: Dict[str, Any],
    owner: str,
    repo: str,
    template_text: str,
) -> str:
    title_val = meta.get("title")
    title = title_val if isinstance(title_val, str) else ""
    description_val = meta.get("description")
    description = description_val if isinstance(description_val, str) else ""
    gh_val = meta.get("github")
    gh_str = gh_val if isinstance(gh_val, str) else ""
    author = parse_github_owner_from_url(gh_str) or ""
    body = template_text
    body = body.replace("{{PLUGIN_MARKER}}", f"{PLUGIN_MARKER_PREFIX}{plugin_name} -->")
    body = body.replace("{{TITLE}}", title.strip() if title else "Plugin")
    body = body.replace("{{DESCRIPTION_BLOCK}}", description.strip())
    body = body.replace("{{INDEX_ENTRY_URL}}", f"https://github.com/{owner}/{repo}/tree/main/plugins/{plugin_name}")
    body = body.replace("{{PLUGIN_REPO_LINK_LINE}}", f"- Plugin repository: {gh_str.strip()}" if gh_str else "")
    body = body.replace("{{AUTHOR_LINE}}", f"- Author: @{author}" if author else "")
    if DISCUSSION_MARKER not in body:
        body = f"{DISCUSSION_MARKER}\n{body.lstrip()}"
    return body.strip() + "\n"


def compile_catalog_index(
    repo_root: Path,
    *,
    owner: str,
    repo: str,
    ref: str = "main",
    existing_index: Optional[Dict[str, Any]] = None,
    discussion_url_fn: Optional[Callable[[str], str]] = None,
) -> Dict[str, Any]:
    """Compile l'index complet du catalogue `plugins/` + `authors/` avec tri canonique."""
    plugins_dir = repo_root / "plugins"
    index: Dict[str, Any] = {
        "version": 1,
        "plugins": dict((existing_index or {}).get("plugins") or {}),
    }
    index["authors"] = read_authors(repo_root / "authors")

    all_rel_paths = [
        p.relative_to(repo_root).as_posix()
        for p in sorted(plugins_dir.rglob("*"))
        if p.is_file()
    ]
    names = resolve_plugin_names(all_paths=all_rel_paths)
    for plugin_name in names:
        if plugin_blocked(plugins_dir, plugin_name):
            remove_index_plugin(index, plugin_name)
            continue
        if plugin_exists(plugins_dir, plugin_name):
            meta = read_plugin_yaml(plugins_dir, plugin_name)
            disc_url = (
                discussion_url_fn(plugin_name)
                if discussion_url_fn is not None
                else f"https://github.com/{owner}/{repo}/discussions/{plugin_name}"
            )
            entry = index_plugin_entry(
                plugin_name, meta, disc_url, repo_root=repo_root, owner=owner, repo=repo, ref=ref
            )
            upsert_index_plugin(index, plugin_name, entry)
        else:
            remove_index_plugin(index, plugin_name)

    index["plugins"] = {k: index["plugins"][k] for k in sorted(index["plugins"].keys())}
    return index


# ===========================================================================
# 4. Orphelins & Stats/Étoiles (find_orphan_plugin_names.py + update_index_stars.py)
# ===========================================================================


def discussion_marker_name(body: str) -> Optional[str]:
    match = PLUGIN_MARKER_RE.search(body)
    if not match:
        return None
    plugin_name = match.group(1).strip()
    return plugin_name or None


def find_orphan_names(
    index: Dict[str, Any],
    plugins_dir: Path,
    discussion_marker_names: Sequence[str] = (),
) -> List[str]:
    plugins = index.get("plugins") if isinstance(index, dict) else {}
    index_names = {
        k.strip()
        for k in (plugins.keys() if isinstance(plugins, dict) else ())
        if isinstance(k, str) and k.strip()
    }
    candidates = sorted(index_names | set(discussion_marker_names))
    return [n for n in candidates if is_valid_plugin_dirname(n) and not plugin_exists(plugins_dir, n)]


def chunks(items: Sequence[Any], n: int) -> List[List[Any]]:
    return [list(items[i : i + n]) for i in range(0, len(items), n)]


def extract_alias_errors(parsed: Dict[str, Any]) -> Dict[str, str]:
    errors = parsed.get("errors")
    if not isinstance(errors, list):
        return {}
    out: Dict[str, str] = {}
    for e in errors:
        if not isinstance(e, dict):
            continue
        path = e.get("path")
        if not isinstance(path, list) or not path:
            continue
        alias = path[0]
        if not isinstance(alias, str):
            continue
        msg = e.get("message")
        if isinstance(msg, str) and msg.strip():
            out[alias] = msg.strip()
    return out


def extract_plugin_version(plugin_yaml_text: str) -> Optional[str]:
    match = re.search(r"(?m)^version\s*:\s*(['\"]?)([^'\"#\n]+)\1\s*(?:#.*)?$", plugin_yaml_text)
    if not match:
        return None
    version = match.group(2).strip()
    return version or None


def extract_commit_info(repo_obj: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    default_branch_ref = repo_obj.get("defaultBranchRef")
    if not isinstance(default_branch_ref, dict):
        return None
    target = default_branch_ref.get("target")
    if not isinstance(target, dict):
        return None
    oid = target.get("oid")
    committed_date = target.get("committedDate")
    if not isinstance(oid, str) or not oid or not isinstance(committed_date, str) or not committed_date:
        return None
    return oid, committed_date


def apply_star_updates(index: Dict[str, Any], updates: Dict[str, Any]) -> int:
    plugins = index.get("plugins")
    if not isinstance(plugins, dict):
        raise UpdateStarsError("index.json.plugins must be an object")
    applied = 0
    for plugin_name, upd in updates.items():
        if not isinstance(plugin_name, str) or not isinstance(upd, dict):
            continue
        entry = plugins.get(plugin_name)
        if not isinstance(entry, dict):
            continue
        stars = upd.get("stars")
        if isinstance(stars, int):
            entry["stars"] = stars
        version = upd.get("version")
        if isinstance(version, str) and version:
            entry["version"] = version
        commit = upd.get("commit")
        if isinstance(commit, str) and commit:
            entry["commit"] = commit
        updated = upd.get("updated")
        if isinstance(updated, str) and updated:
            entry["updated"] = updated
        applied += 1
    index["plugins"] = {k: plugins[k] for k in sorted(plugins.keys())}
    return applied


# ===========================================================================
# 5. Machine à états publication & reprise d'index (publish/download_index_release.py)
# ===========================================================================


def _rel_req_json(
    method: str,
    url: str,
    *,
    token: str,
    opener: Callable[..., Any],
    fail_fn: Callable[[str], NoReturn],
    user_agent: str,
    body: Optional[Dict[str, Any]] = None,
    allow_404: bool = False,
) -> Optional[Dict[str, Any]]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": user_agent,
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with opener(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if allow_404 and e.code == 404:
            return None
        msg = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        fail_fn(f"GitHub API request failed ({e.code}) {method} {url}: {msg}")
    except Exception as e:
        fail_fn(f"GitHub API request failed {method} {url}: {e}")

    if not payload.strip():
        return {}
    try:
        parsed = json.loads(payload)
    except Exception as e:
        fail_fn(f"GitHub API returned invalid JSON for {url}: {e}: {payload[:500]}")
    if not isinstance(parsed, dict):
        fail_fn(f"GitHub API returned non-object JSON for {url}")
    return cast(Dict[str, Any], parsed)


def _fail_pub(msg: str) -> NoReturn:
    raise PublishReleaseError(msg)


def _fail_dl(msg: str) -> NoReturn:
    raise DownloadIndexError(msg)


def _pub_delete_asset(owner: str, repo: str, asset_id: int, *, token: str, opener: Callable[..., Any]) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/assets/{asset_id}"
    req = urllib.request.Request(
        url,
        method="DELETE",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "a0-plugins-index-publisher",
        },
    )
    try:
        with opener(req, timeout=30):
            return
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        err = PublishReleaseError(f"GitHub API request failed ({e.code}) DELETE {url}: {msg}")
    except Exception as e:
        err = PublishReleaseError(f"GitHub API request failed DELETE {url}: {e}")
    if _rel_req_json("GET", url, token=token, opener=opener, fail_fn=_fail_pub, user_agent="a0-plugins-index-publisher", allow_404=True) is not None:
        raise err


def _pub_rename_asset(
    owner: str, repo: str, asset_id: int, name: str, *, token: str, opener: Callable[..., Any], sleep_fn: Callable[[float], Any]
) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/assets/{asset_id}"
    for attempt in range(3):
        try:
            asset = _rel_req_json("GET", url, token=token, opener=opener, fail_fn=_fail_pub, user_agent="a0-plugins-index-publisher")
            assert asset is not None
            if asset.get("name") == name:
                return
            asset = _rel_req_json("PATCH", url, token=token, opener=opener, fail_fn=_fail_pub, user_agent="a0-plugins-index-publisher", body={"name": name})
            assert asset is not None
            if asset.get("name") != name:
                _fail_pub(f"Asset rename did not return the expected name: {name}")
            return
        except PublishReleaseError:
            if attempt == 2:
                raise
            sleep_fn(2)


def publish_index_release(
    index_path: Path,
    *,
    owner: str,
    repo: str,
    token: str,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleep_fn: Callable[[float], Any] = time.sleep,
    tag: str = DEFAULT_RELEASE_TAG,
    release_name: str = DEFAULT_RELEASE_NAME,
    asset_name: str = DEFAULT_ASSET_NAME,
    target: str = "main",
) -> int:
    if not token:
        _fail_pub("GITHUB_TOKEN is required")
    if not index_path.exists():
        return 0
    content = index_path.read_bytes()
    try:
        index = json.loads(content)
    except ValueError as e:
        _fail_pub(f"Invalid index JSON: {e}")
    if not isinstance(index, dict) or not isinstance(index.get("plugins"), dict) or not index["plugins"]:
        _fail_pub("Refusing to publish an index without a non-empty plugins object")

    rel = _rel_req_json(
        "GET",
        f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{urllib.parse.quote(tag)}",
        token=token,
        opener=opener,
        fail_fn=_fail_pub,
        user_agent="a0-plugins-index-publisher",
        allow_404=True,
    )
    if not rel:
        rel = _rel_req_json(
            "POST",
            f"https://api.github.com/repos/{owner}/{repo}/releases",
            token=token,
            opener=opener,
            fail_fn=_fail_pub,
            user_agent="a0-plugins-index-publisher",
            body={
                "tag_name": tag,
                "target_commitish": target,
                "name": release_name,
                "body": "Automated index release asset.",
                "draft": False,
                "prerelease": False,
                "generate_release_notes": False,
            },
        )
    assert rel is not None
    rid = rel.get("id")
    if not isinstance(rid, int):
        _fail_pub("Release id missing")

    release = _rel_req_json(
        "GET",
        f"https://api.github.com/repos/{owner}/{repo}/releases/{rid}",
        token=token,
        opener=opener,
        fail_fn=_fail_pub,
        user_agent="a0-plugins-index-publisher",
    )
    assert release is not None
    assets = {a["name"]: a for a in release.get("assets", [])}
    next_name = f"{asset_name}.next"
    previous_name = f"{asset_name}.previous"
    current = assets.get(asset_name)

    if current is None:
        for name in (next_name, previous_name):
            asset = assets.get(name)
            if asset and asset.get("state") == "uploaded" and asset.get("size", 0) > 0:
                _pub_rename_asset(owner, repo, asset["id"], asset_name, token=token, opener=opener, sleep_fn=sleep_fn)
                current = assets.pop(name)
                break

    if next_name in assets:
        _pub_delete_asset(owner, repo, assets[next_name]["id"], token=token, opener=opener)

    upload_url_tmpl = release.get("upload_url")
    if not isinstance(upload_url_tmpl, str) or "{" not in upload_url_tmpl:
        _fail_pub("Release upload_url missing")
    up_url = upload_url_tmpl.split("{", 1)[0] + "?" + urllib.parse.urlencode({"name": next_name})
    up_req = urllib.request.Request(
        up_url,
        data=content,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "a0-plugins-index-publisher",
            "Content-Type": "application/octet-stream",
        },
    )
    try:
        with opener(up_req, timeout=60) as resp:
            up_payload = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        _fail_pub(f"Asset upload failed ({e.code}) POST {up_url}: {msg}")
    except Exception as e:
        _fail_pub(f"Asset upload failed POST {up_url}: {e}")
    try:
        staged = json.loads(up_payload)
    except ValueError as e:
        _fail_pub(f"Asset upload returned invalid JSON: {e}")
    if (
        not isinstance(staged, dict)
        or not isinstance(staged.get("id"), int)
        or staged.get("name") != next_name
        or staged.get("state") != "uploaded"
        or staged.get("size") != len(content)
    ):
        _fail_pub(f"Asset upload was not complete: {next_name}")

    if current and previous_name in assets:
        _pub_delete_asset(owner, repo, assets[previous_name]["id"], token=token, opener=opener)

    try:
        if current:
            _pub_rename_asset(owner, repo, current["id"], previous_name, token=token, opener=opener, sleep_fn=sleep_fn)
        _pub_rename_asset(owner, repo, staged["id"], asset_name, token=token, opener=opener, sleep_fn=sleep_fn)
    except PublishReleaseError:
        if current:
            try:
                _pub_rename_asset(owner, repo, current["id"], asset_name, token=token, opener=opener, sleep_fn=sleep_fn)
            except PublishReleaseError:
                pass
        raise
    return 0


def download_index_release(
    index_path: Path,
    *,
    owner: str,
    repo: str,
    token: str,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleep_fn: Callable[[float], Any] = time.sleep,
    tag: str = DEFAULT_RELEASE_TAG,
    asset_name: str = DEFAULT_ASSET_NAME,
) -> int:
    if not token:
        _fail_dl("GITHUB_TOKEN is required")
    rel = _rel_req_json(
        "GET",
        f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{urllib.parse.quote(tag)}",
        token=token,
        opener=opener,
        fail_fn=_fail_dl,
        user_agent="a0-plugins-index-downloader",
        allow_404=True,
    )
    if not rel:
        _fail_dl(f"Release tag '{tag}' not found. Generate/publish index.json first.")
    assets = rel.get("assets")
    if not isinstance(assets, list):
        _fail_dl("Release response missing assets")

    download_url: Optional[str] = None
    for name in (asset_name, f"{asset_name}.next", f"{asset_name}.previous"):
        for a in assets:
            if not isinstance(a, dict):
                continue
            if (
                a.get("name") == name
                and a.get("state") == "uploaded"
                and isinstance(a.get("id"), int)
                and isinstance(a.get("browser_download_url"), str)
            ):
                download_url = f"{a['browser_download_url']}?asset_id={a['id']}"
                break
        if download_url:
            break
    if not download_url:
        _fail_dl(f"Release '{tag}' does not contain asset '{asset_name}'")

    req = urllib.request.Request(
        download_url,
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/octet-stream",
            "User-Agent": "a0-plugins-index-downloader",
        },
    )
    content: Optional[bytes] = None
    last_error: Optional[Exception] = None
    for attempt in range(1, 4):
        try:
            with opener(req, timeout=60) as resp:
                content = resp.read()
                break
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
            should_retry = e.code >= 500 or e.code == 429
            last_error = DownloadIndexError(f"Download failed ({e.code}) GET {download_url}: {msg}")
            if should_retry and attempt < 3:
                sleep_fn(5)
                continue
            raise last_error
        except Exception as e:
            last_error = e
            if attempt < 3:
                sleep_fn(5)
                continue
            _fail_dl(f"Download failed GET {download_url}: {e}")
    if content is None:
        if isinstance(last_error, DownloadIndexError):
            raise last_error
        _fail_dl(f"Download failed GET {download_url}: {last_error}")

    try:
        index = json.loads(content)
    except ValueError as e:
        _fail_dl(f"Invalid index JSON: {e}")
    if not isinstance(index, dict) or not isinstance(index.get("plugins"), dict) or not index["plugins"]:
        _fail_dl("Downloaded index must contain a non-empty plugins object")
    index_path.write_bytes(content)
    return 0


# ===========================================================================
# 6. Audit du catalogue & hygiène Agent Zero (aspace_a0_plugins_adapter)
# ===========================================================================


def audit_plugin_catalog(root: Path) -> Dict[str, Any]:
    """Mesure au fichier les 235 dossiers plugins/, les 230 indexés et l'hygiène Agent Zero."""
    plugins = root / "plugins"
    dirs = sorted(p for p in plugins.iterdir() if p.is_dir()) if plugins.is_dir() else []
    resolved = [p for p in dirs if PLUGIN_DIRNAME_PATTERN.fullmatch(p.name) and not p.name.startswith("_")]
    with_index = [p for p in dirs if (p / INDEX_YAML_NAME).exists()]
    legacy = [p.name for p in dirs if not (p / INDEX_YAML_NAME).exists() and (p / "plugin.yaml").exists()]
    blocked = [p.name for p in dirs if (p / BLOCKED_MD_NAME).exists()]
    indexed = [p for p in resolved if p.name not in blocked]
    missing_keys: Dict[str, List[str]] = {k: [] for k in REQUIRED_INDEX_KEYS}
    invalid_yaml: List[str] = []
    max_screenshots = 0
    for p in with_index:
        text = (p / INDEX_YAML_NAME).read_text(encoding="utf-8", errors="replace")
        if not re.search(r"(?m)^[A-Za-z_][A-Za-z0-9_-]*:", text):
            invalid_yaml.append(p.name)
            continue
        for key in REQUIRED_INDEX_KEYS:
            if not re.search(rf"(?m)^{key}:", text):
                missing_keys[key].append(p.name)
        m = re.search(r"(?m)^screenshots:\s*$", text)
        if m:
            block = text[m.end() :]
            count = len(re.findall(r"(?m)^\s+-\s+\S", block.split("\n\n")[0]))
            max_screenshots = max(max_screenshots, count)
    thumbs_dir = root / "generated" / "thumbnails"
    generated = sorted(p.name for p in thumbs_dir.iterdir() if p.is_dir()) if thumbs_dir.is_dir() else []
    orphan_thumbs = [t for t in generated if t not in {p.name for p in dirs}]
    local_thumb = [
        p.name
        for p in with_index
        if any(next(p.glob(f"*{suffix}"), None) is not None for suffix in ALLOWED_IMAGE_EXTS_ORDER)
    ]
    without_thumb = [
        p.name for p in with_index if p.name not in generated and p.name not in local_thumb
    ]
    names = {p.name for p in dirs}
    missing_clean = {k: v for k, v in missing_keys.items() if v}
    abandoned_present = [n for n in ABANDONED_AGENT_ZERO if n in names]
    surfaces_present = [n for n in SURFACES_AGENT_ZERO if n in names]
    return {
        "plugin_dirs_total": len(dirs),
        "plugin_names_resolved": len(resolved),
        "indexed_plugins": len(indexed),
        "index_yaml_present": len(with_index),
        "legacy_plugin_yaml_only": legacy,
        "blocked_plugins": blocked,
        "index_yaml_invalid": invalid_yaml,
        "index_yaml_missing_keys": missing_clean,
        "max_screenshots": max_screenshots,
        "generated_thumbnails": len(generated),
        "orphan_thumbnails": orphan_thumbs,
        "local_thumbnails": len(local_thumb),
        "plugins_without_any_thumbnail": without_thumb,
        "abandoned_present": abandoned_present,
        "surfaces_present": surfaces_present,
        "index_coherent": (
            invalid_yaml == []
            and missing_clean == {}
            and without_thumb == []
            and abandoned_present == []
            and surfaces_present == []
        ),
    }


# ===========================================================================
# 7. Auto-test interne L0 & Reçu R10 mesuré (zéro auto-certification)
# ===========================================================================


def run_plugin_registry_self_test(
    head_sha40: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Vérifie le câblage K2 PluginRegistry sur entrées synthétiques sans auto-certification."""
    root = repo_root or WORKSPACE_ROOT
    sha = head_sha40 or ("0" * 40)
    resolved = resolve_plugin_names(
        all_paths=["plugins/alpha/index.yaml", "plugins/_reserved/index.yaml", "plugins/bad-dash/index.yaml"]
    )
    if resolved != ["alpha"]:
        raise ContractViolation("K2", "plugin_resolution", f"attendu ['alpha'], obtenu {resolved}")
    validate_fields(
        {"title": "Alpha", "description": "Valid entry.", "github": "https://github.com/org/alpha"},
        "alpha",
    )

    evt, rec = consign_measured_l0_evidence(
        actor_from="fabricator",
        actor_to="judge",
        dispatch_id="D-PLUGINS-SMOKE",
        payload="K2 PluginRegistry smoke passed (0 source-oracle parities self-claimed)",
        issuer="Kernel K2 (PluginRegistry)",
        mission_prefix="PLUGINS-SMOKE",
        sha=sha,
        proof=["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_plugin_registry_organ.py"],
        summary=f"K2 PluginRegistry smoke PASS; source_oracle_parity=0 at {sha[:7]}",
        repo_root=root,
    )
    return {
        "organ": "aspace_plugin_registry_organ",
        "source_parity_verified": [],
        "l0_seq": evt["seq"],
        "r10_entry_id": rec["entry_id"],
    }


def consign_plugin_registry_parity_receipt(
    module_results: Dict[str, Dict[str, Any]],
    head_sha40: str,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Consigne uniquement la parité source-vs-organe réellement mesurée pour M001 a0-plugins."""
    verified = sorted(
        mid
        for mid, res in module_results.items()
        if res.get("compared_against_source")
        and res.get("cases_compared", 0) > 0
        and res.get("cases_matched") == res.get("cases_compared")
    )
    total_cases = sum(int(res.get("cases_compared", 0)) for res in module_results.values())
    total_matched = sum(int(res.get("cases_matched", 0)) for res in module_results.values())
    evt, rec = consign_measured_l0_evidence(
        actor_from="fabricator",
        actor_to="judge",
        dispatch_id="D-PLUGINS-PARITY",
        payload=f"K2 PluginRegistry differential parity: {verified} ({total_matched}/{total_cases} cases)",
        issuer="Kernel K2 (PluginRegistry)",
        mission_prefix="PLUGINS-PARITY",
        sha=head_sha40,
        proof=["01_Forkable/FKB00_Runtime/00_A0_Core/aspace_plugin_registry_organ.py"],
        summary=f"K2 PluginRegistry measured parity {total_matched}/{total_cases} across {verified} at {head_sha40[:7]}",
        repo_root=repo_root,
    )
    return {
        "verified_modules": verified,
        "cases_matched": total_matched,
        "cases_compared": total_cases,
        "l0_seq": evt["seq"],
        "r10_entry_id": rec["entry_id"],
    }


if __name__ == "__main__":
    print(json.dumps(run_plugin_registry_self_test(), indent=2, ensure_ascii=False))
