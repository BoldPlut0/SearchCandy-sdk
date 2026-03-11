"""
SearchCandy Python SDK — The Hippocampus of AI.

Self-organizing knowledge graph for AI agents.
Save up to 75% of your context window.

Usage:
    from tgm_sdk import TGMClient

    client = TGMClient(base_url="https://api.searchcandy-labs.com", api_key="sk_live_...")
    
    # Sync your files
    client.sync("my-project", files=[
        {"source_id": "auth.py", "content": open("auth.py").read()},
    ])
    
    # Query
    result = client.retrieve("my-project", "How does auth work?")
    print(result["context"])
"""

__version__ = "0.2.0"

from tgm_sdk.client import TGMClient, TGMError

__all__ = ["TGMClient", "TGMError", "__version__"]
