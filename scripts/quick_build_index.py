"""
Quick Index Builder for C-AIRA - Optimized Version
Builds the vector index faster by reducing logging verbosity.
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

def main():
    print("=" * 80)
    print("C-AIRA Quick Index Builder")
    print("=" * 80)
    
    # Validate config
    is_valid, error = Config.validate()
    if not is_valid:
        print(f"❌ Configuration error: {error}")
        return 1
    
    print("✓ Configuration validated\n")
    
    try:
        # Step 1: Load documents
        print("[1/4] Loading documents...")
        loader = DocumentLoader(Config.DATA_DIR)
        documents = loader.load_all()
        print(f"✓ Loaded {len(documents)} documents\n")
        
        # Step 2: Chunk documents
        print("[2/4] Chunking documents...")
        chunker = TextChunker(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        chunks = chunker.chunk_documents(documents)
        print(f"✓ Created {len(chunks)} chunks\n")
        
        # Step 3: Generate embeddings
        print("[3/4] Generating embeddings (this may take a few minutes)...")
        embedder = Embedder()
        chunks_with_embeddings = embedder.embed_chunks(chunks, batch_size=5)
        print(f"✓ Generated {len(chunks_with_embeddings)} embeddings\n")
        
        # Step 4: Create and save index
        print("[4/4] Creating FAISS index...")
        indexer = VectorIndexer()
        indexer.create_index(chunks_with_embeddings)
        indexer.save_index()
        print(f"✓ Index saved to {Config.VECTOR_STORE_DIR}\n")
        
        print("=" * 80)
        print("✅ Index Building Complete!")
        print("=" * 80)
        print(f"\nIndex Statistics:")
        print(f"  - Documents: {len(documents)}")
        print(f"  - Chunks: {len(chunks)}")
        print(f"  - Embeddings: {len(chunks_with_embeddings)}")
        print(f"\nNext step: Run 'streamlit run src/app/streamlit_app.py'")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
