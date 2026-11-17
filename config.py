
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_model():
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),

        # Keep generated responses bounded.
        max_tokens=1200,

        # Do not repeatedly retry quota errors.
        max_retries=0,

        # Avoid requests hanging indefinitely.
        request_timeout=45,
    )
