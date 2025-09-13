from typing import Optional, List, Dict, Any
from PIL import Image
from replicate.client import Client
import io
import json
import hashlib
import os
from pathlib import Path
import threading

import replicate.client

replicate_client: Optional[Client] = None

# Cache file for embeddings
CACHE_FILE = Path(".cache.json")
_cache_lock = threading.Lock()
_in_memory_cache: Dict[str, List[float]] = {}


def _get_cache_key(data: str) -> str:
    """Generate a cache key from data."""
    return hashlib.sha256(data.encode()).hexdigest()


def _load_cache() -> Dict[str, List[float]]:
    """Load cache from file."""
    global _in_memory_cache
    
    with _cache_lock:
        if _in_memory_cache:
            return _in_memory_cache
            
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    _in_memory_cache = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError, PermissionError):
                _in_memory_cache = {}
        else:
            _in_memory_cache = {}
    
    return _in_memory_cache


def _save_cache() -> None:
    """Save cache to file."""
    with _cache_lock:
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(_in_memory_cache, f, indent=2)
        except Exception:
            pass  # Silently fail if cache write fails


def _get_cached_embedding(cache_key: str) -> Optional[List[float]]:
    """Retrieve embedding from cache."""
    cache = _load_cache()
    return cache.get(cache_key)


def _save_embedding_to_cache(cache_key: str, embedding: List[float]) -> None:
    """Save embedding to cache."""
    global _in_memory_cache
    
    with _cache_lock:
        _in_memory_cache[cache_key] = embedding
    
    _save_cache()


def create_replicate_client() -> Client:
    """
    Creates a singleton Replicate client using API key from settings.
    """
    global replicate_client
    if replicate_client is None:
        from .settings import settings

        replicate_client = Client(api_token=settings.replicate_api_key)

    return replicate_client


def generate_embeddings(image: Image.Image) -> List[float]:
    """
    Generate embeddings from a PIL image using a Replicate model.
    Returns a list of floats suitable for Qdrant add_to_qdrant().
    """
    
    # Create cache key from image data
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    image_data = buf.getvalue()
    cache_key = _get_cache_key(f"image_{hashlib.sha256(image_data).hexdigest()}")
    
    # Check cache first
    cached_embedding = _get_cached_embedding(cache_key)
    if cached_embedding:
        print(f"Using cached embedding for image (key: {cache_key[:16]}...)")
        return cached_embedding

    print(f"Generating new embedding for image (key: {cache_key[:16]}...)")
    client = create_replicate_client()

    # Convert PIL image → bytes
    buf.seek(0)

    # ⚠️ Replace model name/version with the embedding model you want
    output = client.run(
        "krthr/clip-embeddings:1c0371070cb827ec3c7f2f28adcdde54b50dcd239aa6faea0bc98b174ef03fb4",
        input={"image": buf},  # example model
    )

    print(output)

    # Replicate returns JSON-like data; for embeddings it's usually a list of floats
    if isinstance(output, dict) and 'embedding' in output:
        # If output is a dict with 'embedding' key
        embedding = output['embedding']
    elif isinstance(output, list):
        # If output is already a list
        embedding = output
    else:
        embedding = []
    
    # Cache the result
    if embedding:
        _save_embedding_to_cache(cache_key, embedding)
        print(f"Cached embedding for image (key: {cache_key[:16]}...)")
    
    return embedding


def generate_text_embeddings(text: str) -> List[float]:
    """
    Generate embeddings from a text string using a Replicate CLIP model.
    Returns a list of floats suitable for Qdrant add_to_qdrant().
    """
    
    # Create cache key from text
    cache_key = _get_cache_key(f"text_{text}")
    
    # Check cache first
    cached_embedding = _get_cached_embedding(cache_key)
    if cached_embedding:
        print(f"Using cached embedding for text: '{text[:50]}...' (key: {cache_key[:16]}...)")
        return cached_embedding

    print(f"Generating new embedding for text: '{text[:50]}...' (key: {cache_key[:16]}...)")
    client = create_replicate_client()

    output = client.run(
        "krthr/clip-embeddings:1c0371070cb827ec3c7f2f28adcdde54b50dcd239aa6faea0bc98b174ef03fb4",
        input={"text": text},
    )

    # Convert output to list
    if isinstance(output, dict) and 'embedding' in output:
        # If output is a dict with 'embedding' key
        embedding = output['embedding']
    elif isinstance(output, list):
        # If output is already a list
        embedding = output
    else:
        embedding = []
    
    # Cache the result
    if embedding:
        _save_embedding_to_cache(cache_key, embedding)
        print(f"Cached embedding for text: '{text[:50]}...' (key: {cache_key[:16]}...)")
    
    return embedding
