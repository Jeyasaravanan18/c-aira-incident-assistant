"""
Retriever for C-AIRA
Orchestrates query embedding and context retrieval.
"""

import json
from typing import List, Dict, Any
from src.ingestion.embedder import Embedder
from src.retrieval.vector_store import VectorStore
from src.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RetrievalResult:
    """Represents a retrieval result with context and sources"""
    
    def __init__(self, query: str, chunks: List[Dict[str, Any]], context: str):
        self.query = query
        self.chunks = chunks
        self.context = context
    
    def get_sources(self) -> List[str]:
        """Get unique source filenames"""
        sources = set()
        for chunk in self.chunks:
            sources.add(chunk['metadata']['filename'])
        return sorted(list(sources))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'query': self.query,
            'num_chunks': len(self.chunks),
            'sources': self.get_sources(),
            'context': self.context,
        }


class Retriever:
    """Retrieves relevant context for queries using RAG"""
    
    def __init__(self):
        """Initialize the retriever"""
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        logger.info("Initialized Retriever")
    
    def load_index(self) -> None:
        """Load the vector index"""
        self.vector_store.load()
        logger.info("Vector index loaded")
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        include_metadata: bool = True
    ) -> RetrievalResult:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            include_metadata: Whether to include metadata in context
        
        Returns:
            RetrievalResult object
        """
        logger.info(f"Retrieving context for query: {query[:100]}...")
        
        # Embed the query
        query_embedding = self.embedder.embed_text(query)
        logger.debug("Query embedded successfully")
        
        # Search for similar chunks
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k or Config.TOP_K_RESULTS
        )
        
        if not results:
            logger.warning("No relevant chunks found")
            return RetrievalResult(
                query=query,
                chunks=[],
                context="No relevant information found in the knowledge base."
            )
        
        # Format context for LLM
        context = self._format_context(results, include_metadata)
        
        logger.info(f"Retrieved {len(results)} relevant chunks")
        return RetrievalResult(query=query, chunks=results, context=context)
    
    def _format_context(self, results: List[Dict[str, Any]], include_metadata: bool = True) -> str:
        """
        Format retrieved chunks into context string for LLM.
        
        Args:
            results: List of search results
            include_metadata: Whether to include source metadata
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            
            # Build context entry
            if include_metadata:
                header = f"[Document {i}] Source: {metadata['filename']} (Type: {metadata['doc_type']})"
                context_parts.append(header)
                context_parts.append("-" * len(header))
            
            # Get chunk text from metadata
            chunk_text = metadata.get('chunk_text', '[Chunk text not available]')
            context_parts.append(chunk_text)
            context_parts.append("")  # Empty line between chunks
        
        return "\n".join(context_parts)
    
    def get_chunk_details(self, result: Dict[str, Any]) -> str:
        """
        Get detailed information about a chunk.
        
        Args:
            result: Search result dictionary
        
        Returns:
            Formatted chunk details
        """
        metadata = result['metadata']
        
        details = f"""
Chunk Details:
- Source: {metadata['filename']}
- Type: {metadata['doc_type']}
- Chunk ID: {metadata['chunk_id']} / {metadata['total_chunks']}
- Tokens: {metadata['token_count']}
- Similarity: {result['similarity']:.3f}
"""
        return details.strip()


if __name__ == "__main__":
    # Test the retriever
    retriever = Retriever()
    retriever.load_index()
    
    # Test queries
    test_queries = [
        "Database connection timeout error",
        "How to restart the application server",
        "API authentication failed",
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"Query: {query}")
        print('=' * 80)
        
        result = retriever.retrieve(query, top_k=3)
        
        print(f"\nFound {len(result.chunks)} relevant chunks")
        print(f"Sources: {', '.join(result.get_sources())}")
        print(f"\nContext Preview:")
        print(result.context[:500] + "..." if len(result.context) > 500 else result.context)
