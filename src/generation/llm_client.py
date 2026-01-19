"""
LLM Client Module for C-AIRA
Handles interactions with AWS Bedrock for text generation.
"""

import json
from typing import List, Dict, Any, Optional, Iterator
import boto3
from botocore.exceptions import ClientError
from src.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """
    Client for AWS Bedrock LLM (Amazon Nova Pro).
    Handles chat completions and response generation.
    """
    
    def __init__(self):
        """Initialize AWS Bedrock client for LLM."""
        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=Config.AWS_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
            )
            self.model_id = Config.BEDROCK_MODEL_ID
            self.temperature = Config.LLM_TEMPERATURE
            self.max_tokens = Config.LLM_MAX_TOKENS
            self.top_p = Config.LLM_TOP_P
            
            logger.info(f"LLM Client initialized with model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None
    ) -> str:
        """
        Generate a response using AWS Bedrock.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            
        Returns:
            Generated text response
        """
        try:
            # Use provided parameters or defaults
            temp = temperature if temperature is not None else self.temperature
            max_tok = max_tokens if max_tokens is not None else self.max_tokens
            top_p_val = top_p if top_p is not None else self.top_p
            
            # Convert messages to Nova format
            system_prompt = ""
            conversation = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                else:
                    conversation.append({
                        "role": msg['role'],
                        "content": [{"text": msg['content']}]
                    })
            
            # Prepare request body for Amazon Nova
            request_body = {
                "messages": conversation,
                "inferenceConfig": {
                    "temperature": temp,
                    "maxTokens": max_tok,
                    "topP": top_p_val
                }
            }
            
            # Add system prompt if present
            if system_prompt:
                request_body["system"] = [{"text": system_prompt}]
            
            # Invoke model
            response = self.client.converse(
                modelId=self.model_id,
                **request_body
            )
            
            # Extract response text
            output_message = response['output']['message']
            response_text = output_message['content'][0]['text']
            
            # Log token usage
            usage = response.get('usage', {})
            input_tokens = usage.get('inputTokens', 0)
            output_tokens = usage.get('outputTokens', 0)
            logger.info(f"Tokens used - Input: {input_tokens}, Output: {output_tokens}")
            
            return response_text
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def generate_with_context(
        self,
        system_prompt: str,
        user_query: str,
        context: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a response with system prompt, context, and user query.
        Convenience method for RAG applications.
        
        Args:
            system_prompt: System instructions
            user_query: User's question
            context: Retrieved context to ground the response
            temperature: Optional temperature override
            
        Returns:
            Generated response
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_query}"}
        ]
        
        return self.generate(messages, temperature=temperature)
    
    def generate_streaming(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Iterator[str]:
        """
        Generate a streaming response using AWS Bedrock.
        
        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Text chunks as they are generated
        """
        try:
            temp = temperature if temperature is not None else self.temperature
            max_tok = max_tokens if max_tokens is not None else self.max_tokens
            
            # Convert messages
            system_prompt = ""
            conversation = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                else:
                    conversation.append({
                        "role": msg['role'],
                        "content": [{"text": msg['content']}]
                    })
            
            # Prepare request
            request_body = {
                "messages": conversation,
                "inferenceConfig": {
                    "temperature": temp,
                    "maxTokens": max_tok
                }
            }
            
            if system_prompt:
                request_body["system"] = [{"text": system_prompt}]
            
            # Invoke with streaming
            response = self.client.converse_stream(
                modelId=self.model_id,
                **request_body
            )
            
            # Stream response
            stream = response.get('stream')
            if stream:
                for event in stream:
                    if 'contentBlockDelta' in event:
                        delta = event['contentBlockDelta']['delta']
                        if 'text' in delta:
                            yield delta['text']
            
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
