"""
TGM Python SDK — Client for the Temporal Graph Memory API.

Usage:
    from tgm_sdk import TGMClient
    
    client = TGMClient(base_url="http://localhost:8000", api_key="tgm_sk_xxx")
    
    # Create a graph
    graph = client.create_graph("my-project")
    
    # Ingest documents
    result = client.ingest(graph["graph_id"], [
        {"content": "...", "title": "readme.md"}
    ])
    
    # Query
    result = client.retrieve(graph["graph_id"], "How does auth work?")
    print(result["context"])
"""
import httpx
from typing import List, Dict, Optional, Any


class TGMError(Exception):
    """Base exception for TGM SDK errors."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"TGM API Error {status_code}: {detail}")


class TGMClient:
    """
    Python client for the TGM API.
    
    Args:
        base_url: The TGM API base URL (e.g., "http://localhost:8000")
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        self._client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)
    
    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an HTTP request and handle errors."""
        response = self._client.request(method, path, **kwargs)
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise TGMError(response.status_code, detail)
        return response.json()
    
    # --- Authentication ---
    
    def signup(self, email: str, password: str, first_name: str = "", last_name: str = "") -> dict:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: Password (min 8 chars, uppercase, lowercase, number, special char)
            first_name: User's first name
            last_name: User's last name
        
        Returns:
            Dict with user_id, email, api_key, confirmed status
        """
        return self._request("POST", "/v1/auth/signup", json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        })
    
    def confirm_signup(self, email: str, code: str) -> dict:
        """
        Confirm registration with verification code sent to email.
        
        Args:
            email: The email used during signup
            code: The verification code from the email
        
        Returns:
            Dict with confirmation status
        """
        return self._request("POST", "/v1/auth/confirm", json={
            "email": email,
            "code": code
        })
    
    def signin(self, email: str, password: str) -> dict:
        """
        Sign in and get API key + access token.
        
        Automatically sets the API key for subsequent requests.
        
        Args:
            email: User's email address
            password: User's password
        
        Returns:
            Dict with user_id, api_key, access_token, refresh_token, expires_in
        """
        result = self._request("POST", "/v1/auth/signin", json={
            "email": email,
            "password": password
        })
        # Auto-set the API key for subsequent requests
        if "api_key" in result and result["api_key"]:
            self._client.headers["X-API-Key"] = result["api_key"]
        return result
    
    def create_api_key(self, name: str = "default") -> dict:
        """
        Create an additional API key.
        
        Args:
            name: A label for the API key
        
        Returns:
            Dict with key_id, api_key, name, created_at
        """
        return self._request("POST", "/v1/auth/keys", json={"name": name})
    
    def list_api_keys(self) -> list:
        """
        List all API keys for the current user.
        
        Returns:
            List of API key objects with key_id, name, prefix, created_at
        """
        return self._request("GET", "/v1/auth/keys")
    
    def revoke_api_key(self, key_id: str) -> dict:
        """
        Revoke an API key.
        
        Args:
            key_id: The ID of the key to revoke
        
        Returns:
            Dict with revocation confirmation
        """
        return self._request("DELETE", f"/v1/auth/keys/{key_id}")
    
    # --- Health ---
    
    def health(self) -> dict:
        """Check API health."""
        return self._request("GET", "/v1/health")
    
    # --- Graph Management ---
    
    def create_graph(self, graph_id: str, name: str = "", description: str = "") -> dict:
        """Create a new graph."""
        return self._request("POST", "/v1/graphs", json={
            "graph_id": graph_id,
            "name": name or graph_id,
            "description": description
        })
    
    def list_graphs(self) -> list:
        """List all graphs."""
        return self._request("GET", "/v1/graphs")
    
    def get_graph(self, graph_id: str) -> dict:
        """Get graph details."""
        return self._request("GET", f"/v1/graphs/{graph_id}")
    
    def delete_graph(self, graph_id: str) -> dict:
        """Delete a graph."""
        return self._request("DELETE", f"/v1/graphs/{graph_id}")
    
    # --- Ingestion ---
    
    def ingest(self, graph_id: str, documents: List[Dict[str, str]]) -> dict:
        """
        Ingest documents into a graph.
        
        Args:
            graph_id: The graph to ingest into
            documents: List of dicts with 'content', 'title', and optional 'source_id'
        
        Returns:
            Dict with node_ids, node_count, processing_time
        """
        return self._request("POST", f"/v1/graphs/{graph_id}/ingest", json={
            "documents": documents
        })
    
    def ingest_text(self, graph_id: str, content: str, title: str, source_id: str = None) -> dict:
        """Convenience method to ingest a single document."""
        doc = {"content": content, "title": title}
        if source_id:
            doc["source_id"] = source_id
        return self.ingest(graph_id, [doc])
    
    def ingest_file(self, graph_id: str, file_path: str) -> dict:
        """Ingest a file by reading its content."""
        import os
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        title = os.path.basename(file_path)
        return self.ingest_text(graph_id, content, title, source_id=title)
    
    # --- Retrieval ---
    
    def retrieve(self, graph_id: str, query: str, target_tick: int = None, 
                 branch_id: str = None, top_k: int = 20, token_limit: int = 8192) -> dict:
        """
        Query the knowledge graph.
        
        Args:
            graph_id: The graph to query
            query: Natural language query
            target_tick: Optional tick for time travel
            branch_id: Optional branch for multiverse queries
            top_k: Number of anchor nodes to find
            token_limit: Max tokens in assembled context
        
        Returns:
            Dict with context, nodes, total_nodes, execution_time
        """
        payload = {"query": query, "top_k": top_k, "token_limit": token_limit}
        if target_tick is not None:
            payload["target_tick"] = target_tick
        if branch_id:
            payload["branch_id"] = branch_id
        return self._request("POST", f"/v1/graphs/{graph_id}/retrieve", json=payload)
    
    # --- Node Operations ---
    
    def get_node(self, graph_id: str, node_id: str) -> dict:
        """Get a specific node."""
        return self._request("GET", f"/v1/graphs/{graph_id}/nodes/{node_id}")
    
    def replace_node(self, graph_id: str, node_id: str, new_contents: List[str]) -> dict:
        """Replace a node with one or more new nodes."""
        return self._request("POST", f"/v1/graphs/{graph_id}/nodes/{node_id}/replace", json={
            "new_contents": new_contents
        })
    
    def delete_node(self, graph_id: str, node_id: str) -> dict:
        """Delete a node (creates void marker)."""
        return self._request("DELETE", f"/v1/graphs/{graph_id}/nodes/{node_id}")
    
    def batch_replace(self, graph_id: str, replacements: List[Dict]) -> dict:
        """
        Atomically replace multiple nodes.
        
        Args:
            replacements: List of {"old_node_id": "...", "new_contents": ["...", "..."]}
        """
        return self._request("POST", f"/v1/graphs/{graph_id}/nodes/batch-replace", json={
            "replacements": replacements
        })
    
    # --- Edge Operations ---
    
    def get_edge(self, graph_id: str, edge_id: str) -> dict:
        """Get a specific edge."""
        return self._request("GET", f"/v1/graphs/{graph_id}/edges/{edge_id}")
    
    def get_node_edges(self, graph_id: str, node_id: str) -> list:
        """Get all edges for a node."""
        return self._request("GET", f"/v1/graphs/{graph_id}/nodes/{node_id}/edges")
    
    # --- Timeline / Branches ---
    
    def get_timeline(self, graph_id: str) -> dict:
        """Get current tick and branches."""
        return self._request("GET", f"/v1/graphs/{graph_id}/timeline")
    
    def create_branch(self, graph_id: str, branch_id: str, name: str, parent_id: str = None) -> dict:
        """Create a new branch."""
        payload = {"branch_id": branch_id, "name": name}
        if parent_id:
            payload["parent_id"] = parent_id
        return self._request("POST", f"/v1/graphs/{graph_id}/branches", json=payload)
    
    def activate_branch(self, graph_id: str, branch_id: str) -> dict:
        """Switch to a branch."""
        return self._request("PUT", f"/v1/graphs/{graph_id}/branches/{branch_id}/activate")
    
    def merge_branch(self, graph_id: str, branch_id: str, target_branch_id: str = None) -> dict:
        """Merge a branch."""
        payload = {}
        if target_branch_id:
            payload["target_branch_id"] = target_branch_id
        return self._request("POST", f"/v1/graphs/{graph_id}/branches/{branch_id}/merge", json=payload)
    
    # --- Query History ---
    
    def get_query_history(self, graph_id: str, limit: int = 10) -> list:
        """Get query history."""
        return self._request("GET", f"/v1/graphs/{graph_id}/queries", params={"limit": limit})
    
    def log_query(self, graph_id: str, query: str, result_node_ids: List[str] = None, metadata: dict = None) -> dict:
        """Log a query."""
        return self._request("POST", f"/v1/graphs/{graph_id}/queries", json={
            "query": query,
            "result_node_ids": result_node_ids or [],
            "metadata": metadata or {}
        })
    
    # --- Admin ---
    
    def export_graph(self, graph_id: str) -> dict:
        """Export graph snapshot."""
        return self._request("POST", f"/v1/graphs/{graph_id}/export")
    
    def compact_graph(self, graph_id: str) -> dict:
        """Compact graph (remove dead data)."""
        return self._request("POST", f"/v1/graphs/{graph_id}/compact")
    
    def get_stats(self, graph_id: str) -> dict:
        """Get detailed graph statistics."""
        return self._request("GET", f"/v1/graphs/{graph_id}/stats")
    
    # --- Cleanup ---
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
