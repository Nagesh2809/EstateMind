


# from langchain_google_genai import ChatGoogleGenerativeAI
# import os
# from dotenv import load_dotenv
# load_dotenv()  

# os.getenv("GOOGLE_API_KEY")
# os.getenv("GEMINI_MODEL")

# api_key = os.getenv("GOOGLE_API_KEY")
# model_name = os.getenv("GEMINI_MODEL") 


# llm = ChatGoogleGenerativeAI(
#                                 model= model_name, 
#                                 temperature=0.7
#                             )




from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()  

os.getenv("GOOGLE_API_KEY")
os.getenv("GEMINI_MODEL")

# openai/gpt-oss-20b:free
# nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
# minimax/minimax-m3:free

api_key = os.getenv("API_KEY")
model_name = os.getenv("MODEL_NAME") 


llm = ChatOpenAI(
        # model=model_name,
        model = "minimax/minimax-m3:free",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
    )