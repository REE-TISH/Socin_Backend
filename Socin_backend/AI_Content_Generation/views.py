from django.http import StreamingHttpResponse,HttpRequest
from celery import shared_task # For background worker task
from Novel_Content.models import Novel
from google import genai
from google.genai import types
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse,JsonResponse
from Novel_Content.views import is_Premium
from .helpers import EnhanceUserPrompt,is_proper_query,Client,Summarize_Chapter_Content
from .system_prompts import System_prompt_for_eidting_and_creating_chapter
from .models import ChapterBeingCreated
from Custom_user.helpers import user_request_eligible
import time
from .helpers import API_LIST
from typing import List,Dict

User = get_user_model() # User model

# Create your views here.

arr = ['message_1','message_2','message_3','message_4','__DONE__']

# Test view for testing SSE
def testing_AI_Response(request:HttpRequest)->StreamingHttpResponse:

    def event_stream():
        for i in arr:
            time.sleep(1)
            yield f"data: {i}\n\n"
    
    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream")



# Main AI Content generating function
def get_ai_response(request:HttpRequest,novel_id:str)->StreamingHttpResponse:
        novel: Novel = get_object_or_404(Novel,id=novel_id) 
        user = novel.created_by
        user_query: str = request.GET.get('user_query') # User prompt
        # chapter_number = novel.novel_chapter.all().count() #total number of chapters belong to this novel
        working_chapter = ChapterBeingCreated.objects.filter(user=user,novel=novel).order_by('-id').first()
        GEMINI_API_KEY = None
        for i in API_LIST:
            try:
                client = genai.Client(api_key=i)
                response = client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents="generate some content of 50 words to check if this api key is working or not",
                )
                if response.text:
                    GEMINI_API_KEY = i
                    break
            except Exception as e:
                print(f"API key {i} is not working. Error: {e}")
        client = genai.Client(api_key=GEMINI_API_KEY)
        # Event Sending Function
        def event_stream():
            enhanced_prompt:str = user_query
            content:str = ""
            result:Dict[str,object] = is_proper_query(
                user_query,GEMINI_API_KEY,
                working_chapter.content if working_chapter else "", # Checking if the prompt is related to the story
                True if working_chapter else False
            ) 
            if not user_request_eligible(user):
                yield f"data: ERROR: Limit reached\n\n"
                return
            if not result['is_chapter_related']:
                print("Improper query") 
                yield f"data: ERROR: Please rephrase your query. Reason: {result['reason']  }\n\n"
                yield f"data: __DONE__\n\n"
                return
            if is_Premium(user):
                enhanced_prompt = EnhanceUserPrompt(user_query,novel,True if working_chapter else False,working_chapter.content if working_chapter else "") # Enhance the user prompt if its a premium user
                
            system_prompt:str = System_prompt_for_eidting_and_creating_chapter(
                novel,
                enhanced_prompt,
                True if working_chapter else False,
                working_chapter
            )
            
            # Stream the generated content
            try:
                print("####ENHANCED PROMPT",enhanced_prompt)
                response = client.models.generate_content_stream(
                    model="gemini-2.5-flash",
                    contents=[system_prompt],
                )
                
                for chunk in response:
                    print(chunk.text)
                    if chunk.text:
                        content  += f"{chunk.text}"
                        yield f"data: {chunk.text}\n\n"

                yield "data: __DONE__\n\n"  

            except Exception as e:
                yield f"data: ERROR: {str(e)}\n\n"
                print("!!!Error in generating content stream:", e)
                return 
            
            # Store the working chapter content in DB
            if Summarize_Chapter_Content(content,GEMINI_API_KEY,novel,user):
                yield f"data: Chapter content saved successfully.\n\n"
            else:
                yield f"data: ERROR: Failed to save chapter content.\n\n"
            
        return StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream"
        )


