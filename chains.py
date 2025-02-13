import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")

    def extract_relevant_info(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            Clean, examine and extract text. 
            ### VALID JSON (NO PREAMABLE):
            """
        )

        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse message.")
        return res if isinstance(res, list) else [res]
    
    def write_reply(self, message, links):
        prompt_message = PromptTemplate.from_template(
            """
            ### REPLY MESSAGE:
            {message}

            ### INSTRUCTION:
            List of instructions.
            ### MESSAGE (NO PREAMBLE):

            """
        )
        chain_message = prompt_message | self.llm
        res = chain_message.invoke({"message": str(message), "sources": links})
        return res.content
    
if __name__ == "__main__":
    os.getenv("GROQ_API_KEY")