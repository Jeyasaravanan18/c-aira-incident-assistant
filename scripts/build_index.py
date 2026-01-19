"""
Build Vector Index Script
Loads documents, chunks them, generates embeddings, and creates FAISS index.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config
from src.ingestion.document_loader import DocumentLoader
from src.ingestion.chunker import TextChunker
from src.ingestion.embedder import Embedder
from src.ingestion.indexer import VectorIndexer
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main function to build the vector index"""
    
    print("=" * 80)
    print("C-AIRA Vector Index Builder")
    print("=" * 80)
    print()
    
    # Validate configuration
    is_valid, error_msg = Config.validate()
    if not is_valid:
        logger.error(f"Configuration validation failed: {error_msg}")
        print(f"\n❌ Error: {error_msg}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Set all required Azure OpenAI credentials")
        print("3. Configured deployment names correctly")
        return 1
    
    print("✓ Configuration validated")
    print(Config.get_summary())
    
    try:
        # Step 1: Load documents
        print("\n" + "=" * 80)
        print("Step 1: Loading Documents")
        print("=" * 80)
        
        loader = DocumentLoader(Config.DATA_DIR)
        documents = loader.load_all()
        
        if not documents:
            logger.error("No documents found to index")
            print("\n❌ Error: No documents found in data directory")
            print(f"\nPlease add documents to:")
            print(f"  - {os.path.join(Config.DATA_DIR, 'incidents')}")
            print(f"  - {os.path.join(Config.DATA_DIR, 'runbooks')}")
            print(f"  - {os.path.join(Config.DATA_DIR, 'logs')}")
            return 1
        
        print(f"\n✓ Loaded {len(documents)} documents")
        
        # Step 2: Chunk documents
        print("\n" + "=" * 80)
        print("Step 2: Chunking Documents")
        print("=" * 80)
        
        chunker = TextChunker(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        chunks = chunker.chunk_documents(documents)
        
        stats = chunker.get_chunk_stats(chunks)
        print(f"\n✓ Created {stats['total_chunks']} chunks")
        print(f"  - Average tokens per chunk: {stats['avg_tokens']:.1f}")
        print(f"  - Min tokens: {stats['min_tokens']}")
        print(f"  - Max tokens: {stats['max_tokens']}")
        
        # Step 3: Generate embeddings
        print("\n" + "=" * 80)
        print("Step 3: Generating Embeddings")
        print("=" * 80)
        print("\nThis may take a few minutes depending on the number of chunks...")
        
        embedder = Embedder()
        embeddings = embedder.embed_chunks(chunks)
        
        print(f"\n✓ Generated {len(embeddings)} embeddings")
        print(f"  - Embedding dimension: {len(embeddings[0])}")
        
        # Step 4: Create and save index
        print("\n" + "=" * 80)
        print("Step 4: Creating FAISS Index")
        print("=" * 80)
        
        indexer = VectorIndexer()
        indexer.create_index(embeddings, chunks)
        indexer.save_index()
        
        index_stats = indexer.get_stats()
        print(f"\n✓ Index created and saved")
        print(f"  - Total vectors: {index_stats['total_vectors']}")
        print(f"  - Dimension: {index_stats['dimension']}")
        print(f"  - Index path: {Config.FAISS_INDEX_PATH}")
        print(f"  - Metadata path: {Config.METADATA_PATH}")
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ Index Building Complete!")
        print("=" * 80)
        print("\nYou can now run the C-AIRA application:")
        print("  streamlit run src/app/streamlit_app.py")
        print()
        
        return 0
        
    except Exception as e:
        logger.error(f"Index building failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check the logs for more details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
