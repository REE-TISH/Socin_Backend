from django.http import StreamingHttpResponse,HttpRequest
from celery import shared_task
from Novel_Content.models import get_chapter_summary,Novel,Chapter
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from django.http import HttpResponse,JsonResponse
from Novel_Content.views import is_Premium
from .helpers import EnhanceUserPrompt,is_proper_query,Client
from .system_prompts import System_prompt_for_eidting_and_creating_chapter
from .models import ChapterBeingCreated
from Custom_user.helpers import increment_user_request_count,user_request_eligible
from decouple import config
import time
import json
from .helpers import API_LIST
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


# Data structure for extra chapter content 
class Content_and_Summary(BaseModel):
    """A data structure for storing content and its summary."""
    chapter_name:str = Field(description="based on the summary give the chapter a suitable name ")
    summary: str = Field(description="Just give the main points so that you could understand these later or even some keyword for you to understand as you have to read these later without reaching the context window limit")
    ultra_short_summary:str = Field(description="this is the ultra short summary that will be stored for keeping the context of the full story")


# Main AI Content generating function
def get_ai_response(request:HttpRequest,novel_id:str)->StreamingHttpResponse:
        novel = get_object_or_404(Novel,id=novel_id) 
        user = novel.created_by
        user_query = request.GET.get('user_query') # User prompt
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
            enhanced_prompt = user_query
            content = ""
            result = is_proper_query(user_query,novel,GEMINI_API_KEY) # Checking if the prompt is related to the story
            if not user_request_eligible(user):
                yield f"data: ERROR: Limit reached\n\n"
                return
            if not result:
                print("Improper query")
                yield f"data: ERROR: Improper query. Please rephrase your query.\n\n"
                yield f"data: __DONE__\n\n"
                return
            if is_Premium(user):
                enhanced_prompt = EnhanceUserPrompt(user_query,novel,True if working_chapter else False)
            system_prompt = System_prompt_for_eidting_and_creating_chapter(novel,enhanced_prompt,working_chapter)

            # Stream the generated content
            try:
                response = client.models.generate_content_stream(
                    model="gemini-2.5-flash",
                    contents= system_prompt,)

                for chunk in response:
                    
                    if chunk.text:
                        content  += f"{chunk.text}"
                        yield f"data: {chunk.text}\n\n"

                yield "data: __DONE__\n\n"

            except Exception as e:
                yield f"data: ERROR: {str(e)}\n\n"
                return 
            
            # Generate extra chapter content
            chapter_content = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=f"SYSTEM: You are an AI novel summarizer expert , Your job is to summarize the given content in as small context as possible with keeping the meaning of that novel chapter so that it could be used for the creation of furthur chapters . HERE IS THE NOVEL CHAPTER THAT YOU HAVE TO WORK UPON: {content}",
                config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=Content_and_Summary,
                )
            )
            dictionary_chapter_content = json.loads(chapter_content.text)
            increment_user_request_count(user)
            # Save the Current Chapter User working on in DB
            ChapterBeingCreated.objects.get_or_create(
                user=user,
                novel=novel,
                content=content,
                chapter_name=dictionary_chapter_content['chapter_name'],
                chapter_summary=dictionary_chapter_content['summary'],
                ultra_short_summary=dictionary_chapter_content['ultra_short_summary'],
            )

        return StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream"
        )


