"""
Text Chunker for C-AIRA
Implements semantic chunking with token-based splitting and overlap.
"""

from typing import List, Dict, Any
import tiktoken
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TextChunk:
    """Represents a chunk of text with metadata"""
    
    def __init__(self, text: str, metadata: Dict[str, Any], chunk_id: int):
        self.text = text
        self.metadata = metadata
        self.chunk_id = chunk_id
    
    def __repr__(self):
        return f"TextChunk(id={self.chunk_id}, tokens={self.metadata.get('token_count')})"


class TextChunker:
    """Chunks documents into smaller pieces with overlap"""
    
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 50, encoding_name: str = "cl100k_base"):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Target size of each chunk in tokens
            chunk_overlap: Number of overlapping tokens between chunks
            encoding_name: Tiktoken encoding name (cl100k_base for GPT-4)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            logger.warning(f"Failed to load encoding {encoding_name}, using default: {e}")
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        logger.info(f"Initialized TextChunker (size={chunk_size}, overlap={chunk_overlap})")
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text: Input text
        
        Returns:
            Token count
        """
        return len(self.encoding.encode(text))
    
    def chunk_document(self, document) -> List[TextChunk]:
        """
        Chunk a document into smaller pieces.
        
        Args:
            document: Document object with content and metadata
        
        Returns:
            List of TextChunk objects
        """
        text = document.content
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)
        
        logger.info(f"Chunking document: {document.metadata.get('filename')} ({total_tokens} tokens)")
        
        chunks = []
        chunk_id = 0
        start_idx = 0
        
        while start_idx < total_tokens:
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.chunk_size, total_tokens)
            
            # Extract chunk tokens
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Create chunk metadata (inherit from document + add chunk-specific info)
            chunk_metadata = document.metadata.copy()
            chunk_metadata.update({
                'chunk_id': chunk_id,
                'start_token': start_idx,
                'end_token': end_idx,
                'token_count': len(chunk_tokens),
                'total_chunks': None,  # Will be set after all chunks are created
            })
            
            chunks.append(TextChunk(
                text=chunk_text,
                metadata=chunk_metadata,
                chunk_id=chunk_id
            ))
            
            chunk_id += 1
            
            # Move start index forward (with overlap)
            start_idx = end_idx - self.chunk_overlap
            
            # Prevent infinite loop if overlap >= chunk_size
            if start_idx <= end_idx - self.chunk_size:
                start_idx = end_idx
        
        # Update total_chunks in metadata
        for chunk in chunks:
            chunk.metadata['total_chunks'] = len(chunks)
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def chunk_documents(self, documents: List) -> List[TextChunk]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of Document objects
        
        Returns:
            List of all TextChunk objects
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def get_chunk_stats(self, chunks: List[TextChunk]) -> Dict[str, Any]:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of TextChunk objects
        
        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {}
        
        token_counts = [chunk.metadata['token_count'] for chunk in chunks]
        
        stats = {
            'total_chunks': len(chunks),
            'avg_tokens': sum(token_counts) / len(token_counts),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts),
            'total_tokens': sum(token_counts),
        }
        
        return stats


if __name__ == "__main__":
    # Test the chunker
    from src.ingestion.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    documents = loader.load_all()
    
    chunker = TextChunker(chunk_size=600, chunk_overlap=50)
    chunks = chunker.chunk_documents(documents)
    
    stats = chunker.get_chunk_stats(chunks)
    print(f"\nChunking Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
