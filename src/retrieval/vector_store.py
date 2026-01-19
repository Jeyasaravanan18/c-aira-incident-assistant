"""
Vector Store for C-AIRA
Handles FAISS index operations and similarity search.
"""

import numpy as np
from typing import List, Tuple, Dict, Any
from src.ingestion.indexer import VectorIndexer
from src.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Manages vector storage and similarity search"""
    
    def __init__(self):
        """Initialize the vector store"""
        self.indexer = VectorIndexer()
        self.loaded = False
        logger.info("Initialized VectorStore")
    
    def load(self, index_path: str = None, metadata_path: str = None) -> None:
        """
        Load the vector index from disk.
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSON file
        """
        try:
            self.indexer.load_index(index_path, metadata_path)
            self.loaded = True
            logger.info("Vector store loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load vector store: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (optional)
        
        Returns:
            List of search results with scores and metadata
        """
        if not self.loaded:
            raise RuntimeError("Vector store not loaded. Call load() first.")
        
        if self.indexer.index is None:
            raise RuntimeError("No index available")
        
        # Use config defaults if not provided
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        if similarity_threshold is None:
            similarity_threshold = Config.SIMILARITY_THRESHOLD
        
        # Convert query to numpy array
        query_array = np.array([query_embedding], dtype=np.float32)
        
        # Search in FAISS index
        # Note: FAISS returns L2 distances, lower is better
        distances, indices = self.indexer.index.search(query_array, top_k)
        
        # Convert distances to similarity scores (inverse of L2 distance)
        # Normalize to 0-1 range where 1 is most similar
        max_distance = np.max(distances[0]) if np.max(distances[0]) > 0 else 1.0
        similarities = 1 - (distances[0] / max_distance)
        
        # Build results
        results = []
        for idx, (index, distance, similarity) in enumerate(zip(indices[0], distances[0], similarities)):
            # Skip invalid indices
            if index < 0 or index >= len(self.indexer.metadata):
                continue
            
            # Apply similarity threshold
            if similarity < similarity_threshold:
                logger.debug(f"Skipping result {idx} (similarity {similarity:.3f} < threshold {similarity_threshold})")
                continue
            
            result = {
                'rank': idx + 1,
                'index': int(index),
                'distance': float(distance),
                'similarity': float(similarity),
                'metadata': self.indexer.metadata[index],
            }
            results.append(result)
        
        logger.info(f"Found {len(results)} results above threshold {similarity_threshold}")
        return results
    
    def get_chunk_text(self, result: Dict[str, Any]) -> str:
        """
        Get the text content for a search result.
        Note: This requires the chunks to be stored or re-loaded.
        For now, we'll return a placeholder.
        
        Args:
            result: Search result dictionary
        
        Returns:
            Chunk text
        """
        # In a production system, you might store chunk texts separately
        # or retrieve them from the original documents
        return result['metadata'].get('text', '[Text not available]')
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.loaded:
            return {'status': 'Not loaded'}
        
        return self.indexer.get_stats()


if __name__ == "__main__":
    # Test the vector store
    from src.ingestion.embedder import Embedder
    
    # Load vector store
    store = VectorStore()
    store.load()
    
    # Test search with a sample query
    embedder = Embedder()
    query = "Database connection timeout error"
    query_embedding = embedder.embed_text(query)
    
    results = store.search(query_embedding, top_k=3)
    
    print(f"\nSearch Results for: '{query}'")
    for result in results:
        print(f"\nRank {result['rank']}:")
        print(f"  Similarity: {result['similarity']:.3f}")
        print(f"  Source: {result['metadata']['filename']}")
        print(f"  Type: {result['metadata']['doc_type']}")
