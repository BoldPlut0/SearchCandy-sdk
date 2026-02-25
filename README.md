# TGM SDK — Python Client for Temporal Graph Memory

A lightweight Python SDK for interacting with the [TGM API](https://tgm.dev) — a self-organizing knowledge graph database.

## Installation

```bash
pip install tgm-sdk
```

Or install from source:

```bash
pip install git+https://github.com/BoldPlut0/SearchCandy-sdk.git
```

## Quick Start

```python
from tgm_sdk import TGMClient

# Connect to TGM API
client = TGMClient(base_url="https://api.tgm.dev", api_key="tgm_sk_xxx")

# Create a knowledge graph
graph = client.create_graph("my-project", name="My Project")

# Ingest documents
client.ingest(graph["graph_id"], [
    {"content": "Your document text here...", "title": "readme.md"}
])

# Query the graph
result = client.retrieve(graph["graph_id"], "How does authentication work?")
print(result["context"])  # Assembled context from the knowledge graph
print(result["nodes"])    # Evidence nodes with sources
```

## Features

- **Ingest** any text, code, logs, or documents into a self-organizing knowledge graph
- **Retrieve** context using physics-based graph traversal
- **Mutate** nodes (replace, delete) with automatic edge inheritance
- **Time Travel** — query the graph at any point in history
- **Branching** — create parallel timelines for A/B testing
- **Multi-graph** — manage multiple independent knowledge graphs

## API Methods

| Method | Description |
|--------|-------------|
| `create_graph()` | Create a new knowledge graph |
| `list_graphs()` | List all graphs |
| `get_graph()` | Get graph details |
| `delete_graph()` | Delete a graph |
| `ingest()` | Ingest documents into a graph |
| `ingest_text()` | Ingest a single text document |
| `ingest_file()` | Ingest a file from disk |
| `retrieve()` | Query the knowledge graph |
| `get_node()` | Get a specific node |
| `replace_node()` | Replace a node with new content |
| `delete_node()` | Delete a node (void marker) |
| `batch_replace()` | Atomically replace multiple nodes |
| `get_edge()` | Get a specific edge |
| `get_node_edges()` | Get all edges for a node |
| `get_timeline()` | Get current tick and branches |
| `create_branch()` | Create a new branch |
| `activate_branch()` | Switch to a branch |
| `merge_branch()` | Merge a branch |
| `get_query_history()` | Get query history |
| `export_graph()` | Export graph snapshot |
| `compact_graph()` | Compact graph storage |
| `get_stats()` | Get graph statistics |

## Context Manager

```python
with TGMClient(base_url="https://api.tgm.dev", api_key="tgm_sk_xxx") as client:
    result = client.retrieve("my-graph", "What is TGM?")
    print(result["context"])
# Connection automatically closed
```

## Error Handling

```python
from tgm_sdk import TGMClient, TGMError, GraphNotFoundError

try:
    client.get_graph("nonexistent")
except GraphNotFoundError as e:
    print(f"Graph not found: {e.detail}")
except TGMError as e:
    print(f"API error {e.status_code}: {e.detail}")
```

## API Reference

See the [full API documentation](https://docs.tgm.dev/api-reference).

## License

MIT
