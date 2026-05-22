from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

gpt_4_1_mini = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    max_tokens=3000,
    max_retries=2,
    timeout=60
)