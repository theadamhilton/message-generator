import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import chromadb
import uuid
from chains import Chain
from utils import clean_text
import logging
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# Initialize Chain for LLM processing
chain = Chain()

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient('vectorstore')
collection = chroma_client.get_or_create_collection(name="messages")

# Initialize Transformers pipeline for intent detection
classifier = pipeline('text-classification', model="Falconsai/intent_classification")

# Set up logging
logging.basicConfig(level=logging.DEBUG)

SIMILARITY_THRESHOLD = 0.65

@app.post("/process")
async def process_data(request: Request):
    """Receives data from PHP, processes it using LLM, stores in ChromaDB, and returns response."""
    data = await request.json()
    
    # Ensure the message key is present
    message = data.get("message")
    if not message:
        return {"error": "No message provided"}

    try:
        # Step 1: Detect the intent of the user message
        intent_label = "unknown" # Default value in case classification fails
        intent = classifier(message)
        
        if isinstance(intent, list) and len(intent) > 0 and 'label' in intent[0]:
            intent_label = intent[0]['label']

        logging.debug("Detected Intent: %s", intent)

        # Step 2: Check for similar messages in ChromaDB
        query_results = collection.query(
                query_texts=[message],
                n_results=1
        )

        # Log the query results
        logging.debug("Query Results: %s", query_results)

        # Check if query results contain documents and have a high similarity score 
        if query_results and 'documents' in query_results and query_results['documents'][0]:
            if query_results['distances'][0][0] < SIMILARITY_THRESHOLD:
                # Use the stored response if a similar message is found with the same intent is found
                stored_metadata = query_results['metadatas'][0][0]
                stored_response = stored_metadata.get('response')
                stored_intent = stored_metadata.get('intent')
                logging.debug("Stored Intent: %s", stored_intent)
                if stored_response and stored_intent == intent_label:
                    return {"response": stored_response, "stored": True, "intent": intent_label}
        
        # Step 3: Clean the input message
        cleaned_message = clean_text(message)

        # Step 4: Extract relevant info using Chain
        extracted_info = chain.extract_relevant_info(cleaned_message)

        # Step 5: Generate final LLM response
        final_reply = chain.write_reply(extracted_info, links=None)

        # Step 6: Store user message & response in ChromaDB
        metadata = {"response": final_reply, "query": message, "intent": intent_label}
        collection.add(
            documents=[cleaned_message], 
            metadatas=[metadata], 
            ids=[str(uuid.uuid4())]
        )
        logging.debug("Stored Metadata: %s", metadata)
        
        # Step 7: Return processed response to PHP
        return {"response": final_reply, "stored": False, "intent": intent_label}

    except Exception as e:
        logging.error("Processing failed: %s", str(e))
        return {"error": f"Processing failed: {str(e)}"}

@app.post("/return")
async def return_data(request: Request):
    """Receives processed data and forwards it to PHP."""
    data = await request.json()

    # Get the processed response from FastAPI processing
    response_text = data.get("response") or data.get("answer")

    if response_text:
        try:
            php_response = requests.post(BACK_URL=str(return_data), json={"response": response_text})
            return php_response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to send data to PHP: {str(e)}"}
    else:
        return {"error": "No response received to send to PHP"}
    
if __name__ == "__main__":
    return_data = os.getenv("BACK_URL")