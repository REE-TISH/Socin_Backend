from langchain.tools import tool
from langchain.chat_models import init_chat_model
from decouple import config

#! USE THIS LATER WHEN THE I WANT A BETTER AI MANAGEMENT SYSTEM AND OUTPUT
#? MORE SCALABLE OPTION BUT FOR NOW STICKING TO SIMPLE CALLING GEMINI API WITH PREVIOUS MEMORY CONTEXT

GEMINI_API_KEY = "AIzaSyDzu1OtMfKTM-V6JpjWVCRkLho2_yibRFw"

model = init_chat_model(
    model_provider='google_genai',
    model="gemini-2.5-flash-lite",
    api_key=GEMINI_API_KEY)

response = model.invoke([
    {"role": "user", "content": "how much could i use google free api key if i am using gemini-2 or 2.5?"}
])

print(response.content)