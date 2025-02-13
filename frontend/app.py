import streamlit as st
import requests

from chains import Chain
from archives.messages import Message
from utils import clean_text

FASTAPI_BACK_URL = "http://127.0.0.1:8000/return"

def create_streamlit_app(llm, messsages, clean_text):
    st.title("Message Generator")

    # Receive search results from FastAPI
    search_result = st.text_area("Received Search Result:")

    if st.button("Process Search Result"):
        if not search_result.strip():
            st.warning("Please provide a search result to process.")
            return

        # Step 1: Extract relevant info
        cleaned_data = chain.extract_relevant_info(search_result)

        # Step 2: Generate final response
        final_reply = chain.write_reply(cleaned_data, links=None)

        # Step 3: Display the cleaned output
        st.write("Processed Response:", final_reply)

        # Step 4: Send cleaned data back to FastAPI
        response = requests.post(FASTAPI_BACK_URL, json={"reply": final_reply})
        if response.status_code == 200:
            st.success("Processed data sent successfully!")
        else:
            st.error(f"Error sending data: {response.text}")


if __name__ == "__main__":
    chain = Chain()
    messages = Message()
    st.set_page_config(layout="wide", page_title="Message Generator")
    create_streamlit_app(chain, messages, clean_text)