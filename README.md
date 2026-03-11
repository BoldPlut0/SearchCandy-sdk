# SearchCandy Python SDK

**The Hippocampus of AI** — Save up to 75% of your context window.

SearchCandy is a self-organizing knowledge graph that gives AI agents instant access to codebases without stuffing the context window. Sync your files, ask questions, get focused context.

## Installation

```bash
pip install searchcandy
```

## Quick Start

```python
from tgm_sdk import TGMClient

# Initialize
client = TGMClient(
    base_url="https://api.searchcandy-labs.com",
    api_key="sk_live_..."
)

# Create a graph for your project
client.create_graph("my-project", name="My Project")

# Sync your files (builds the knowledge graph automatically)
client.sync("my-project", files=[
    {"source_id": "auth.py", "content": open("auth.py").read()},
    {"source_id": "routes.py", "content": open("routes.py").read()},
    {"source_id": "database.py", "content": open("database.py").read()},
])

# Query — get focused context for your AI agent
result = client.retrieve("my-project", "How does JWT authentication work?")
print(result["context"])  # Exact source code chunks, ready for your LLM
```

## Core APIs

### Sync Files (Primary API)

```python
# Sync changed files — only changed parts get re-processed
client.sync("my-project", files=[
    {"source_id": "auth.py", "content": new_content},
])

# Sync a single file
client.sync_file("my-project", "auth.py", new_content)

# Delete a file from the graph
client.sync_delete("my-project", "old_utils.py")

# Sync an entire directory
client.sync_directory("my-project", "./src", extensions=[".py", ".ts"])
```

### Retrieve Context

```python
# Single query
result = client.retrieve("my-project", "How does auth work?")
print(result["context"])       # The context string — feed to your LLM
print(result["total_results"]) # Number of chunks found

# Batch queries (multiple questions at once)
result = client.batch_retrieve("my-project", queries=[
    "How does auth work?",
    "What database tables exist?",
    "What API endpoints are available?",
])
for r in result["results"]:
    print(f"{r['query']}: {len(r['context'])} chars")
```

### Conversation Branching

```python
# Branch from a specific version (like git)
client.sync("my-project", 
    files=[{"source_id": "auth.py", "content": oauth_code}],
    branch_from_version=10, 
    new_branch="try-oauth"
)

# Query on the branch
result = client.retrieve("my-project", "How does auth work?", branch="try-oauth")
# → Returns OAuth code

# Query on main (original code still there)
result = client.retrieve("my-project", "How does auth work?", branch="main")
# → Returns original code
```

### Graph Management

```python
# Create
client.create_graph("my-project", name="My Project", description="...")

# List all graphs
graphs = client.list_graphs()

# Get info
info = client.get_graph("my-project")
print(f"Nodes: {info['node_count']}, Edges: {info['edge_count']}")

# List source files
sources = client.list_sources("my-project")
for s in sources["sources"]:
    print(f"{s['source_id']}: {s['node_count']} chunks")

# Delete
client.delete_graph("my-project")
```

### Version History & Branches

```python
# Get timeline
timeline = client.get_timeline("my-project")
print(f"Version: {timeline['current_tick']}, Branch: {timeline['active_branch']}")

# Create a branch
client.create_branch("my-project", "experiment", name="Experiment Branch")

# Switch branches
client.activate_branch("my-project", "experiment")

# Merge
client.merge_branch("my-project", "experiment")
```

## How It Works

1. **Sync** your files → SearchCandy chunks, embeds, and connects them into a knowledge graph
2. **Query** in natural language → SearchCandy walks the graph and returns focused context (~2-3K chars)
3. **Update** a file → Only the changed parts get re-processed (git-style hash diff)

No schema, no config, no manual chunking. The graph self-organizes from your data.

## Authentication

```python
# Sign up
client.signup("you@company.com", "YourPassword123!")

# Confirm email
client.confirm_signup("you@company.com", "123456")

# Sign in (auto-sets API key for subsequent requests)
client.signin("you@company.com", "YourPassword123!")
```

## Requirements

- Python 3.8+
- `httpx` (installed automatically)

## Links

- [Documentation](https://docs.searchcandy-labs.com)
- [API Reference](https://docs.searchcandy-labs.com/api)
- [GitHub](https://github.com/searchcandy-labs/searchcandy-python)

## License

MIT
