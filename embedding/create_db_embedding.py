import chromadb
import os
from chromadb.utils import embedding_functions

# Configuration of the OpenAI API key
key_openai = os.getenv('KEY_OPENAI')
if key_openai is None:
    raise ValueError("OpenAI API key not found in environment variables.")

# Setting up the ChromaDB client
try:
    chroma_client = chromadb.PersistentClient(path='iap_db')
    # You can change collection: ( 1ca ), ( 2ca ), ( 3ca ), ( 4tx )
    collection = chroma_client.get_or_create_collection(name="3ca")
except Exception as e:
    print(f"Error initializing ChromaDB client: {e}")
    raise

# Initializing the OpenAI embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    model_name="text-embedding-ada-002",
    api_key=key_openai
)

def split_text(text):
    pieces = text.split("###")
    return [piece.strip() for piece in pieces if piece.strip()]

# Reading the text file
try:
    with open('image_processing/Redacted_IEP_3_CA.txt', 'r', encoding="utf-8") as file:
        text = file.read()
except FileNotFoundError:
    print("File '.txt' not found.")
    text = ""

pieces = split_text(text)

for i, piece in enumerate(pieces):
    print(f"Piece {i + 1}:")
    print(piece)
    
    # Obtaining the embedding of the text piece using the ChromaDB embedding function
    try:
        embedding = openai_ef([piece])
        if embedding is not None:
            # Adding the document and its embedding to ChromaDB
            collection.add(documents=[piece], ids=[str(i)], embeddings=[embedding[0]])
            print(f"Embedding for Piece {i + 1} added successfully.")
        else:
            print(f"Failed to obtain embedding for Piece {i + 1}.")
    except Exception as e:
        print(f"Error obtaining embedding for Piece {i + 1}: {e}")

# Closing the ChromaDB client if necessary