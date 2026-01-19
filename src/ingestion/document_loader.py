"""
Document Loader for C-AIRA
Loads text-based documents from structured folders.
"""

import os
from typing import List, Dict, Any
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Document:
    """Represents a loaded document with metadata"""
    
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata
    
    def __repr__(self):
        return f"Document(source={self.metadata.get('source')}, length={len(self.content)})"


class DocumentLoader:
    """Loads documents from the file system"""
    
    SUPPORTED_EXTENSIONS = ['.txt', '.md']
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the document loader.
        
        Args:
            data_dir: Root directory containing document folders
        """
        self.data_dir = data_dir
        logger.info(f"Initialized DocumentLoader with data_dir: {data_dir}")
    
    def load_from_directory(self, directory: str, doc_type: str = "general") -> List[Document]:
        """
        Load all supported documents from a directory.
        
        Args:
            directory: Directory path to load from
            doc_type: Type of documents (incidents, runbooks, logs)
        
        Returns:
            List of Document objects
        """
        documents = []
        
        if not os.path.exists(directory):
            logger.warning(f"Directory does not exist: {directory}")
            return documents
        
        logger.info(f"Loading documents from: {directory}")
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Check file extension
            _, ext = os.path.splitext(filename)
            if ext.lower() not in self.SUPPORTED_EXTENSIONS:
                logger.debug(f"Skipping unsupported file: {filename}")
                continue
            
            try:
                doc = self.load_file(file_path, doc_type)
                documents.append(doc)
                logger.info(f"Loaded: {filename} ({len(doc.content)} chars)")
            except Exception as e:
                logger.error(f"Failed to load {filename}: {str(e)}")
        
        logger.info(f"Loaded {len(documents)} documents from {directory}")
        return documents
    
    def load_file(self, file_path: str, doc_type: str = "general") -> Document:
        """
        Load a single document file.
        
        Args:
            file_path: Path to the file
            doc_type: Type of document
        
        Returns:
            Document object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get file metadata
        stat = os.stat(file_path)
        metadata = {
            'source': file_path,
            'filename': os.path.basename(file_path),
            'doc_type': doc_type,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }
        
        return Document(content=content, metadata=metadata)
    
    def load_all(self) -> List[Document]:
        """
        Load all documents from all subdirectories in data_dir.
        
        Returns:
            List of all Document objects
        """
        all_documents = []
        
        # Define document types and their directories
        doc_categories = {
            'incidents': os.path.join(self.data_dir, 'incidents'),
            'runbooks': os.path.join(self.data_dir, 'runbooks'),
            'logs': os.path.join(self.data_dir, 'logs'),
        }
        
        for doc_type, directory in doc_categories.items():
            docs = self.load_from_directory(directory, doc_type)
            all_documents.extend(docs)
        
        logger.info(f"Total documents loaded: {len(all_documents)}")
        return all_documents


if __name__ == "__main__":
    # Test the document loader
    loader = DocumentLoader()
    documents = loader.load_all()
    
    print(f"\nLoaded {len(documents)} documents:")
    for doc in documents:
        print(f"  - {doc.metadata['filename']} ({doc.metadata['doc_type']})")
