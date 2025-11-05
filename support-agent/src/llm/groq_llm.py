import os
from dotenv import load_dotenv

load_dotenv()

try:
	from langchain_groq import ChatGroq
except Exception as e:
	ChatGroq = None
	print(f"Warning: ChatGroq import failed: {e}")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if ChatGroq is None:
	llm = None
else:
	if not GROQ_API_KEY:
		print("Warning: GROQ_API_KEY not set in environment; llm will be None")
		llm = None
	else:
		try:
			llm = ChatGroq(api_key=GROQ_API_KEY, model_name="openai/gpt-oss-120b")
		except Exception as e:
			print(f"Warning: failed to construct ChatGroq LLM: {e}")
			llm = None
