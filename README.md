# SearchCandy Python SDK

**The Hippocampus of AI** — Save up to 75% of your context window.

SearchCandy is a self-organizing knowledge graph that gives AI agents instant access to codebases without stuffing the context window. Sync your files, ask questions, get focused context.

[![PyPI version](https://badge.fury.io/py/searchcandy.svg)](https://pypi.org/project/searchcandy/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install tgm
```

## Quick Start

```python
from tgm_sdk import TGMClient

client = TGMClient(
    base_url="https://api.searchcandy-labs.com",
    api_key="sk_live_..."
)

# 1. Create a graph
client.create_graph("my-project", name="My Project")

# 2. Sync your files (this is the ONLY API you need for data)
client.sync("my-project", files=[
    {"source_id": "auth.py", "content": open("auth.py").read()},
    {"source_id": "routes.py", "content": open("routes.py").read()},
])

# 3. Query — get focused context for your AI agent
result = client.retrieve("my-project", "How does JWT authentication work?")
print(result["context"])  # 2-3K chars of relevant source code
```

---

## API Reference

### Initialization

```python
client = TGMClient(
    base_url="https://api.searchcandy-labs.com",  # Required
    api_key="sk_live_...",                          # Required for auth-enabled servers
    timeout=60.0                                    # Optional, default 60s
)
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `base_url` | str | Yes | `"http://localhost:8000"` | API server URL |
| `api_key` | str | No | `None` | API key for authentication |
| `timeout` | float | No | `60.0` | Request timeout in seconds |

---

### `sync()` — Sync Files to the Graph

**This is the primary API.** Use it for everything: initial load, updates, deletions, branching.

```python
result = client.sync("my-project", files=[
    {"source_id": "auth.py", "content": "import jwt\n..."},
    {"source_id": "old_utils.py", "action": "delete"},
])
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `graph_id` | str | Yes | — | The graph to sync to |
| `files` | list[dict] | Yes | — | Array of file specs (see below) |
| `branch` | str | No | `None` | Branch to sync to. Default: active branch |
| `branch_from_version` | int | No | `None` | Create a new branch from this version first |
| `new_branch` | str | No | `None` | Name for the new branch (required with `branch_from_version`) |

**File spec:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source_id` | str | Yes | — | Unique file identifier (e.g., `"src/auth.py"`) |
| `content` | str | No* | `""` | Full file content. *Required unless action is `"delete"` |
| `action` | str | No | `"auto"` | One of: `"auto"`, `"create"`, `"delete"`, `"replace_all"` |

**Actions explained:**

| Action | Behavior |
|--------|----------|
| `"auto"` | Smart sync — detects what changed via hash-diff. New files get ingested, existing files get diffed, empty content deletes. |
| `"create"` | Force fresh ingestion. Ignores any existing content for this source. |
| `"delete"` | Delete all nodes from this source. Content field is ignored. |
| `"replace_all"` | Delete all existing content, then re-ingest from scratch. |

**Returns:**

```python
{
    "object": "sync",
    "version": 42,                    # Current graph version after sync
    "branch": "main",                 # Active branch
    "files": {
        "auth.py": {
            "unchanged": 8,           # Chunks with identical content (zero cost)
            "replaced": 2,            # Chunks that were modified
            "added": 1,              # New chunks
            "deleted": 0,            # Removed chunks
            "total_nodes_after": 11  # Total alive chunks for this file
        }
    },
    "total_changes": 3,              # Total changes across all files
    "processing_time_ms": 450
}
```

**Errors:**

| HTTP Code | Error Code | When | Fix |
|-----------|-----------|------|-----|
| 400 | `empty_files` | `files` array is empty | Provide at least one file |
| 400 | `unsupported_content` | Binary content detected (null bytes, >30% non-printable chars) | Only sync text/code files |
| 400 | `future_version` | `branch_from_version` is ahead of current version | Use a version ≤ current |
| 404 | `graph_not_found` | Graph doesn't exist | Create the graph first |
| 500 | `internal_error` | Server-side failure (e.g., embedding service down) | Retry or check server logs |

---

### `sync_file()` — Sync a Single File (Convenience)

```python
result = client.sync_file("my-project", "auth.py", new_content)
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `graph_id` | str | Yes | The graph to sync to |
| `source_id` | str | Yes | File identifier |
| `content` | str | Yes | File content |
| `action` | str | No | Default: `"auto"` |

---

### `sync_delete()` — Delete a File (Convenience)

```python
result = client.sync_delete("my-project", "old_utils.py")
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `graph_id` | str | Yes | The graph |
| `source_id` | str | Yes | File to delete |

---

### `sync_directory()` — Sync an Entire Directory

```python
result = client.sync_directory("my-project", "./src", extensions=[".py", ".ts"])
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `graph_id` | str | Yes | — | The graph |
| `directory` | str | Yes | — | Path to directory |
| `extensions` | list[str] | No | `[".py", ".js", ".ts", ".md", ...]` | File extensions to include |

---

### `retrieve()` — Query the Graph

```python
result = client.retrieve("my-project", "How does authentication work?")
context = result["context"]  # Feed this to your LLM
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `graph_id` | str | Yes | — | The graph to query |
| `query` | str | Yes | — | Natural language question |
| `branch` | str | No | `None` | Branch to query (default: active) |
| `version` | int | No | `None` | Version for time travel queries |
| `max_context_chars` | int | No | `3500` | Max characters in returned context |

**Returns:**

```python
{
    "object": "retrieval",
    "query": "How does authentication work?",
    "context": "<context_layer>...[actual source code]...</context_layer>",
    "results": [
        {
            "node_id": "abc123",
            "id": "abc123",
            "content": "def create_token(user_id)...",
            "content_type": "source_code",
            "source": "auth.py",
            "relevance": 0.82,
            "version": 5,
            "branch": "main"
        }
    ],
    "total_results": 7,
    "search_info": {
        "candidates_found": 20,
        "candidates_selected": 7,
        "sources_used": ["auth.py", "routes.py"],
        "connection_types": ["sequential", "cross_document"],
        "off_topic_rejected": false
    },
    "execution_time_ms": 111
}
```

**Errors:**

| HTTP Code | Error Code | When | Fix |
|-----------|-----------|------|-----|
| 400 | `empty_query` | Query is empty or whitespace | Provide a non-empty query |
| 400 | `invalid_target_tick` | `version` is negative | Use version ≥ 0 |
| 404 | `graph_not_found` | Graph doesn't exist | Create the graph first |
| 500 | `retrieval_failed` | Embedding server unreachable or index error | Check embedding service |

**Off-topic behavior:** If the query is unrelated to the graph content (e.g., "chocolate cake recipe" on a code graph), `total_results` will be 0 and `context` will be empty. This is correct — the system returns nothing rather than hallucinating.

---

### `batch_retrieve()` — Multi-Query

```python
result = client.batch_retrieve("my-project", queries=[
    "How does auth work?",
    "What database tables exist?",
    "What API endpoints are available?",
])
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `graph_id` | str | Yes | — | The graph |
| `queries` | list[str] | Yes | — | Array of questions |
| `branch` | str | No | `None` | Branch to query |
| `version` | int | No | `None` | Version for time travel |
| `max_context_chars` | int | No | `3500` | Max chars per query |

**Returns:**

```python
{
    "object": "batch_retrieval",
    "results": [
        {"query": "How does auth work?", "context": "...", "total_results": 7, "execution_time_ms": 95},
        {"query": "What database tables exist?", "context": "...", "total_results": 5, "execution_time_ms": 88},
        {"query": "What API endpoints?", "context": "...", "total_results": 8, "execution_time_ms": 92}
    ],
    "total_execution_time_ms": 275
}
```

**Errors:**

| HTTP Code | Error Code | When | Fix |
|-----------|-----------|------|-----|
| 400 | `empty_query` | Queries array is empty | Provide at least one query |
| 404 | `graph_not_found` | Graph doesn't exist | Create the graph first |

---

### `list_sources()` — List Files in Graph

```python
result = client.list_sources("my-project")
for source in result["sources"]:
    print(f"{source['source_id']}: {source['node_count']} chunks")
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `graph_id` | str | Yes | The graph |

**Returns:**

```python
{
    "object": "sources",
    "graph_id": "my-project",
    "sources": [
        {"source_id": "auth.py", "node_count": 5, "content_types": ["source_code"],
         "earliest_version": 1, "latest_version": 10},
        {"source_id": "routes.py", "node_count": 8, "content_types": ["source_code"],
         "earliest_version": 1, "latest_version": 5}
    ],
    "total_sources": 2
}
```

---

### `create_graph()` — Create a New Graph

```python
graph = client.create_graph("my-project", name="My Project", description="Project docs")
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `graph_id` | str | Yes | — | Unique graph identifier. Letters, numbers, underscores, hyphens only. |
| `name` | str | No | Same as graph_id | Human-readable name |
| `description` | str | No | `""` | Description |

**Returns:**

```python
{
    "object": "graph",
    "graph_id": "my-project",
    "name": "My Project",
    "description": "Project docs",
    "node_count": 0,
    "edge_count": 0,
    "current_tick": 0,
    "active_branch": "main",
    "created_at": 1710000000.0
}
```

**Errors:**

| HTTP Code | Error Code | When | Fix |
|-----------|-----------|------|-----|
| 400 | `invalid_graph_id` | Graph ID contains special characters | Use only letters, numbers, `_`, `-` |
| 409 | `graph_already_exists` | A graph with this ID already exists | Choose a different ID or delete the existing one |

---

### `get_graph()` — Get Graph Info

```python
info = client.get_graph("my-project")
print(f"Nodes: {info['node_count']}, Version: {info['current_tick']}")
```

**Errors:**

| HTTP Code | Error Code | When | Fix |
|-----------|-----------|------|-----|
| 404 | `graph_not_found` | Graph doesn't exist | Create it first |

---

### `list_graphs()` — List All Graphs

```python
graphs = client.list_graphs()
for g in graphs:
    print(f"{g['graph_id']}: {g['node_count']} nodes")
```

Returns a list. Never errors (returns empty list if no graphs).

---

### `delete_graph()` — Delete a Graph

```python
client.delete_graph("my-project")
```

⚠️ **This is permanent.** All nodes, edges, versions, and branches are deleted.

**Errors:**

| HTTP Code | Error Code | When | Fix |
|-----------|-----------|------|-----|
| 404 | `graph_not_found` | Graph doesn't exist | Already deleted or never created |

---

### `get_timeline()` — Version and Branch Info

```python
timeline = client.get_timeline("my-project")
print(f"Version: {timeline['current_tick']}, Branch: {timeline['active_branch']}")
print(f"Branches: {[b['branch_id'] for b in timeline['branches']]}")
```

---

### `create_branch()` — Create a Branch

```python
client.create_branch("my-project", "experiment", name="Experiment Branch")
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `graph_id` | str | Yes | — | The graph |
| `branch_id` | str | Yes | — | Unique branch identifier |
| `name` | str | Yes | — | Human-readable branch name |
| `parent_id` | str | No | Active branch | Parent branch to fork from |

**Errors:**

| HTTP Code | Error Code | When | Fix |
|-----------|-----------|------|-----|
| 400 | `branch_already_exists` | Branch ID already taken | Choose a different name |

---

### `activate_branch()` — Switch to a Branch

```python
client.activate_branch("my-project", "experiment")
# All subsequent sync/retrieve calls use this branch
```

**Errors:**

| HTTP Code | Error Code | When | Fix |
|-----------|-----------|------|-----|
| 404 | `branch_not_found` | Branch doesn't exist | Create it first |

---

### `merge_branch()` — Merge a Branch

```python
result = client.merge_branch("my-project", "experiment")
print(f"Merged {result['merged_nodes']} nodes")
```

---

### `health()` — Check API Status

```python
status = client.health()
# {"object": "health", "status": "healthy", "version": "0.1.0"}
```

---

## Error Handling

All errors are raised as `TGMError` with HTTP status code and detail message:

```python
from tgm_sdk import TGMClient, TGMError

client = TGMClient(api_key="sk_live_...")

try:
    result = client.retrieve("my-project", "How does auth work?")
except TGMError as e:
    print(f"Status: {e.status_code}")
    print(f"Detail: {e.detail}")
```

### Error Code Reference

| HTTP | Code | Description |
|------|------|-------------|
| 400 | `empty_files` | Sync: files array is empty |
| 400 | `empty_query` | Retrieve: query is empty |
| 400 | `unsupported_content` | Sync: binary content detected |
| 400 | `future_version` | Sync: branch_from_version ahead of current |
| 400 | `invalid_graph_id` | Graph: ID has invalid characters |
| 400 | `invalid_target_tick` | Retrieve: negative version number |
| 401 | `missing_api_key` | No X-API-Key header provided |
| 403 | `invalid_api_key` | API key is invalid or expired |
| 404 | `graph_not_found` | Graph doesn't exist |
| 404 | `node_not_found` | Node doesn't exist |
| 404 | `edge_not_found` | Edge doesn't exist |
| 404 | `branch_not_found` | Branch doesn't exist |
| 409 | `graph_already_exists` | Graph with this ID already exists |
| 429 | `rate_limit_exceeded` | Too many requests per minute |
| 500 | `internal_error` | Server error (check logs) |
| 500 | `retrieval_failed` | Retrieval pipeline error |

---

## Typical Agent Integration

```python
from tgm_sdk import TGMClient

# Initialize once
tgm = TGMClient(api_key="sk_live_...")

# Day 1: Load the project
tgm.create_graph("my-project", name="My Project")
tgm.sync_directory("my-project", "./src")

# Every file change:
tgm.sync_file("my-project", "src/auth.py", open("src/auth.py").read())

# Every question:
result = tgm.retrieve("my-project", user_question)
context = result["context"]
# Feed context to your LLM

# User goes back to try a different approach:
tgm.sync("my-project",
    files=[{"source_id": "src/auth.py", "content": new_approach_code}],
    branch_from_version=10,
    new_branch="try-oauth"
)

# Query the experiment:
result = tgm.retrieve("my-project", "How does auth work?", branch="try-oauth")
```

## Requirements

- Python 3.8+
- `httpx` (installed automatically)

## Links

- [Documentation](https://docs.searchcandy-labs.com)
- [API Reference](https://docs.searchcandy-labs.com/api)
- [GitHub](https://github.com/BoldPlut0/SearchCandy-sdk)

## License

MIT — see [LICENSE](LICENSE)
