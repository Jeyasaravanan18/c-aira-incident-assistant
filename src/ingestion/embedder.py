"""
Embedder Module for C-AIRA
Generates embeddings using AWS Bedrock Titan Embeddings.
"""

import json
import time
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from src.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Embedder:
    """
    Handles embedding generation using AWS Bedrock Titan Embeddings.
    """
    
    def __init__(self):
        """Initialize AWS Bedrock client for embeddings."""
        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=Config.AWS_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
            )
            self.model_id = Config.BEDROCK_EMBEDDING_MODEL_ID
            logger.info(f"Embedder initialized with model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def embed_text(self, text: str, max_retries: int = 3) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of floats representing the embedding vector
        """
        for attempt in range(max_retries):
            try:
                # Prepare request body for Titan Embeddings
                request_body = json.dumps({
                    "inputText": text
                })
                
                # Invoke model
                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=request_body,
                    contentType='application/json',
                    accept='application/json'
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                embedding = response_body.get('embedding')
                
                if not embedding:
                    raise ValueError("No embedding in response")
                
                return embedding
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ThrottlingException' and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff
                    logger.warning(f"Rate limited, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Bedrock API error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Error generating embedding: {e}")
                raise
        
        raise Exception(f"Failed to generate embedding after {max_retries} attempts")
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 10,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once (for rate limiting)
            show_progress: Whether to log progress
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)
        
        logger.info(f"Generating embeddings for {total} texts...")
        
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            for text in batch:
                embedding = self.embed_text(text)
                batch_embeddings.append(embedding)
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            
            embeddings.extend(batch_embeddings)
            
            if show_progress:
                progress = min(i + batch_size, total)
                logger.info(f"Progress: {progress}/{total} embeddings generated")
        
        logger.info(f"✓ Generated {len(embeddings)} embeddings")
        return embeddings
    
    def embed_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            batch_size: Batch size for processing
            
        Returns:
            List of chunks with added 'embedding' field
        """
        logger.info(f"Embedding {len(chunks)} chunks...")
        
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embed_batch(texts, batch_size=batch_size)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding
        
        logger.info(f"✓ All chunks embedded successfully")
        return chunks
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension (1024 for Titan Text Embeddings V2)
        """
        # Titan Text Embeddings V2 produces 1024-dimensional vectors by default
        return 1024
