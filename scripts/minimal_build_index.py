"""
Minimal Index Builder - Skips slow chunking by using simple text splitting
"""
import json
import os
import sys
import numpy as np
import faiss
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple configuration from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"

def simple_chunk_text(text, chunk_size=500):
    """Simple character-based chunking"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        
        if current_length >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def get_embedding(text, client):
    """Get embedding from Bedrock"""
    response = client.invoke_model(
        modelId=EMBEDDING_MODEL,
        body=json.dumps({"inputText": text}),
        contentType='application/json',
        accept='application/json'
    )
    result = json.loads(response['body'].read())
    return result['embedding']

def main():
    print("Starting minimal index builder...")
    
    # Initialize Bedrock client
    client = boto3.client(
        'bedrock-runtime',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    # Load documents
    all_chunks = []
    all_metadata = []
    
    data_dir = "data"
    for folder in ["incidents", "runbooks", "logs"]:
        folder_path = os.path.join(data_dir, folder)
        if not os.path.exists(folder_path):
            continue
            
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if not os.path.isfile(filepath):
                continue
                
            print(f"Processing {filename}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple chunking
            chunks = simple_chunk_text(content, chunk_size=500)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({
                    'filename': filename,
                    'type': folder,
                    'chunk_id': i,
                    'chunk_text': chunk
                })
    
    print(f"\nTotal chunks: {len(all_chunks)}")
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = []
    for i, chunk in enumerate(all_chunks):
        if i % 5 == 0:
            print(f"  Progress: {i}/{len(all_chunks)}")
        emb = get_embedding(chunk, client)
        embeddings.append(emb)
    
    print(f"Generated {len(embeddings)} embeddings")
    
    # Create FAISS index
    print("Creating FAISS index...")
    embeddings_array = np.array(embeddings).astype('float32')
    dimension = embeddings_array.shape[1]
    
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    # Save index
    os.makedirs("vector_store", exist_ok=True)
    faiss.write_index(index, "vector_store/faiss_index")
    
    with open("vector_store/metadata.json", 'w') as f:
        json.dump(all_metadata, f)
    
    print("\n✅ Index created successfully!")
    print(f"  - Chunks: {len(all_chunks)}")
    print(f"  - Dimension: {dimension}")
    print(f"  - Saved to: vector_store/")
    print("\nNext: Run 'streamlit run src/app/streamlit_app.py'")

if __name__ == "__main__":
    main()
