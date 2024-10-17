import chromadb
import os
from chromadb.utils import embedding_functions
from openai import OpenAI
import json

# Configure the OpenAI API key
key_openai = os.getenv('KEY_OPENAI')
if key_openai is None:
    raise ValueError("OpenAI API key not found in environment variables.")

# Initialize the OpenAI client
client = OpenAI(api_key=key_openai)

# Configure the ChromaDB client
try:
    chroma_client = chromadb.PersistentClient(path='iap_db')
    # You can change collection: ( 1ca ), ( 2ca ), ( 3ca ), ( 4tx )
    collection_name = "1ca"  # Store the collection name
    collection = chroma_client.get_collection(name=collection_name)
except Exception as e:
    print(f"Error initializing ChromaDB client: {e}")
    raise

# Initialize the OpenAI embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    model_name="text-embedding-ada-002",
    api_key=key_openai
)

def search_documents(query, top_k=5):
    # Obtain the embedding of the query
    embedding_query = openai_ef([query])
    
    if embedding_query is None or not embedding_query:
        print("Failed to obtain embedding for the query.")
        return []

    # Searching for the most relevant documents
    results = collection.query(
        query_embeddings=embedding_query[0],
        n_results=top_k
    )
    
    return results

def generate_openai_response(client, content, question):
    try:
        conclusion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                        You are an IEP (Individualized Education Program) assistant. Your role is to provide clear and concise answers to any questions from families of children completing IEP documents. Respond with a JSON format containing the student's goals, but without summarizing, as shown in the example below:
                        {
                            "goal1": "The student needs help in mathematics.",
                            "goal2": "The student needs help in Geography.",
                            "goal3": "The student needs help with inclusion."
                        }
                        Maintain a supportive and empathetic tone during your interactions.
                    """
                },
                {"role": "system", "content": content},  # Document content
                {"role": "user", "content": question},  # User's question
            ],
            temperature=0
        )
        
        raw_response = conclusion.choices[0].message.content
        
        # Clean the response to ensure it's a valid JSON
        raw_response = raw_response.replace('```json', '').replace('```', '').strip()  # Remove formatting
        raw_response = raw_response.strip()  # Remove whitespace
        
        # Attempt to convert the response to JSON
        response_json = json.loads(raw_response)
        return response_json
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return {"error": "Sorry, I couldn't generate a response in JSON format."}
    except Exception as e:
        print(f"Error generating response: {e}")
        return {"error": "Sorry, I couldn't generate a response at this time."}
    
def save_response_to_json(response, collection_name):
    filename = f"{collection_name}.json"  # Use the collection name in the filename
    try:
        with open(filename, 'w') as json_file:
            json.dump(response, json_file, indent=4)
        print(f"Response saved to {filename}")
    except Exception as e:
        print(f"Error saving response to JSON file: {e}")
    
# Example usage
if __name__ == "__main__":
    while True:
        query = input("Enter your query ('exit' to quit): ")
        if query.lower() == 'exit':
            print("Exiting the program.")
            break

        results = search_documents(query)
        
        if 'documents' in results:
            first_doc = results['documents'][0]
            content = " ".join(first_doc)
            question = query
            
            # After generating the response
            response = generate_openai_response(client, content, question)

            # Save the response to a JSON file using the collection name
            save_response_to_json(response, collection_name)  # Pass collection_name

            print(f"{response}\n")
        else:
            print("No documents found for the query.")