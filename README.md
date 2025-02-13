## AutoBot: Message Generator

AutoBot: Message Generator is an advanced tool designed for seamless information retrieval. Users can enter their queries on various platforms such as web and mobile to receive insights on any topic of their choosing.


## Features

Versatile Query Input: Users can type their questions anywhere, whether on web or mobile, to gain insights.

Backend Integration: Efficiently extracts information from backend servers, returning it to the client.

Developer Ready Chatbot: Developers can implement AutoBot as a chatbot after Streamlit testing.

Intent Classification: Utilizes Hugging Face Transformer's Falconsai model for precise intent recognition.

Text Processing: Employs Llama 3.3 LLM for accurate and context-aware responses.

Efficient Indexing: ChromaDB indexing is used for easy storage and rapid retrieval of frequently asked questions.


## Installation

To get started we first need to get an API_KEY from here: https://console.groq.com/keys. Inside app/.env update the value of GROQ_API_KEY with the API_KEY you created.

###
To get started, first install the dependencies using:

    pip install -r requirements.txt

###
Run the Streamlit app or FastAPI app:

    streamlit run app/main.py
    uvicorn main:app --reload