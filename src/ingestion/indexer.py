"""
Indexer for C-AIRA
Creates and persists FAISS vector index.
"""

import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any
from src.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VectorIndexer:
    """Creates and manages FAISS vector index"""
    
    def __init__(self):
        """Initialize the vector indexer"""
        self.index = None
        self.metadata = []
        logger.info("Initialized VectorIndexer")
    
    def create_index(self, embeddings: List[List[float]], chunks: List) -> None:
        """
        Create FAISS index from embeddings.
        
        Args:
            embeddings: List of embedding vectors
            chunks: List of TextChunk objects (for metadata)
        """
        if len(embeddings) != len(chunks):
            raise ValueError("Number of embeddings must match number of chunks")
        
        logger.info(f"Creating FAISS index with {len(embeddings)} vectors...")
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        dimension = embeddings_array.shape[1]
        
        logger.info(f"Embedding dimension: {dimension}")
        
        # Create FAISS index (using L2 distance)
        # For production, consider using IndexIVFFlat for larger datasets
        self.index = faiss.IndexFlatL2(dimension)
        
        # Add vectors to index
        self.index.add(embeddings_array)
        
        # Store metadata with chunk text
        self.metadata = []
        for chunk in chunks:
            metadata = chunk.metadata.copy()
            metadata['chunk_text'] = chunk.text  # Store the actual text
            self.metadata.append(metadata)
        
        logger.info(f"FAISS index created with {self.index.ntotal} vectors")
    
    def save_index(self, index_path: str = None, metadata_path: str = None) -> None:
        """
        Save FAISS index and metadata to disk.
        
        Args:
            index_path: Path to save FAISS index
            metadata_path: Path to save metadata JSON
        """
        if self.index is None:
            raise ValueError("No index to save. Create index first.")
        
        # Use default paths if not provided
        if index_path is None:
            index_path = Config.FAISS_INDEX_PATH
        if metadata_path is None:
            metadata_path = Config.METADATA_PATH
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        logger.info(f"FAISS index saved to: {index_path}")
        
        # Save metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
        logger.info(f"Metadata saved to: {metadata_path}")
    
    def load_index(self, index_path: str = None, metadata_path: str = None) -> None:
        """
        Load FAISS index and metadata from disk.
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSON file
        """
        # Use default paths if not provided
        if index_path is None:
            index_path = Config.FAISS_INDEX_PATH
        if metadata_path is None:
            metadata_path = Config.METADATA_PATH
        
        # Check if files exist
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        logger.info(f"FAISS index loaded from: {index_path} ({self.index.ntotal} vectors)")
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        logger.info(f"Metadata loaded from: {metadata_path} ({len(self.metadata)} entries)")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary with index statistics
        """
        if self.index is None:
            return {'status': 'No index loaded'}
        
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.index.d,
            'metadata_count': len(self.metadata),
        }


if __name__ == "__main__":
    # Test the indexer
    from src.ingestion.document_loader import DocumentLoader
    from src.ingestion.chunker import TextChunker
    from src.ingestion.embedder import Embedder
    
    # Load, chunk, and embed documents
    loader = DocumentLoader()
    documents = loader.load_all()
    
    chunker = TextChunker()
    chunks = chunker.chunk_documents(documents)
    
    embedder = Embedder()
    embeddings = embedder.embed_chunks(chunks)
    
    # Create and save index
    indexer = VectorIndexer()
    indexer.create_index(embeddings, chunks)
    indexer.save_index()
    
    print(f"\nIndex Statistics:")
    for key, value in indexer.get_stats().items():
        print(f"  {key}: {value}")
