"""
Configuration Management for C-AIRA
Loads and validates environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for C-AIRA"""
    
    # AWS Bedrock Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "eu-north-1")
    
    # Model IDs
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
    BEDROCK_EMBEDDING_MODEL_ID: str = os.getenv("BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")
    
    # Model Configuration
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    LLM_TOP_P: float = float(os.getenv("LLM_TOP_P", "0.95"))
    
    # Chunking Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "600"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # Retrieval Configuration
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # Application Configuration
    APP_TITLE: str = os.getenv("APP_TITLE", "C-AIRA - Context-Aware Incident Response Assistant")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Paths
    DATA_DIR: str = "data"
    VECTOR_STORE_DIR: str = "vector_store"
    FAISS_INDEX_PATH: str = os.path.join(VECTOR_STORE_DIR, "faiss_index")
    METADATA_PATH: str = os.path.join(VECTOR_STORE_DIR, "metadata.json")
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validate that all required configuration is present.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not cls.AWS_ACCESS_KEY_ID:
            return False, "AWS_ACCESS_KEY_ID is not set"
        
        if not cls.AWS_SECRET_ACCESS_KEY:
            return False, "AWS_SECRET_ACCESS_KEY is not set"
        
        if not cls.AWS_REGION:
            return False, "AWS_REGION is not set"
        
        if not cls.BEDROCK_MODEL_ID:
            return False, "BEDROCK_MODEL_ID is not set"
        
        if not cls.BEDROCK_EMBEDDING_MODEL_ID:
            return False, "BEDROCK_EMBEDDING_MODEL_ID is not set"
        
        # Validate chunk configuration
        if cls.CHUNK_SIZE <= 0:
            return False, "CHUNK_SIZE must be positive"
        
        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            return False, "CHUNK_OVERLAP must be less than CHUNK_SIZE"
        
        # Validate retrieval configuration
        if cls.TOP_K_RESULTS <= 0:
            return False, "TOP_K_RESULTS must be positive"
        
        if not 0 <= cls.SIMILARITY_THRESHOLD <= 1:
            return False, "SIMILARITY_THRESHOLD must be between 0 and 1"
        
        return True, None
    
    @classmethod
    def get_summary(cls) -> str:
        """Get a summary of current configuration (without sensitive data)"""
        return f"""
Configuration Summary:
- AWS Region: {cls.AWS_REGION}
- LLM Model: {cls.BEDROCK_MODEL_ID}
- Embedding Model: {cls.BEDROCK_EMBEDDING_MODEL_ID}
- Chunk Size: {cls.CHUNK_SIZE} tokens
- Chunk Overlap: {cls.CHUNK_OVERLAP} tokens
- Top-K Results: {cls.TOP_K_RESULTS}
- Similarity Threshold: {cls.SIMILARITY_THRESHOLD}
- Temperature: {cls.LLM_TEMPERATURE}
"""


# Validate configuration on import
is_valid, error_msg = Config.validate()
if not is_valid and os.path.exists(".env"):
    # Only warn if .env exists (not during initial setup)
    import warnings
    warnings.warn(f"Configuration validation failed: {error_msg}")
