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
from .helpers import EnhanceUserPrompt,is_proper_query
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


# Main response generating function
def get_ai_response(request:HttpRequest,novel_id:str)->StreamingHttpResponse:
        novel = get_object_or_404(Novel,id=novel_id) 
        user = novel.created_by
        user_query = request.GET.get('user_query') # User prompt
        # chapter_number = novel.novel_chapter.all().count() #total number of chapters belong to this novel
        working_chapter = ChapterBeingCreated.objects.filter(user=user,novel=novel).order_by('-id').first()
        enhanced_prompt = user_query
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
        
        if is_Premium(user) and user_request_eligible(user):
            response = EnhanceUserPrompt(user_query,novel,GEMINI_API_KEY,True if working_chapter else False)

        SYSTEM_PROMPT_FOR_CREATING_NEW_CHAPTER = f"""
                !!! You just have to create novel , DO NOT write anything uneccesaary like :
                                I have created this or anything or give me more context Just give answer if not much context given then assume take any famous novel and combine it what few bits of information you have from user
                    SYSTEM: 
                        You are a professional novelist AI whose single purpose is to produce long-form fiction with exceptional storytelling, broad perspective, and airtight internal logic. Always behave like a senior author/editor who plans novels before writing scenes. Follow these rules for every request unless the user explicitly overrides them:

                        Understand the mission first — before drafting, silently generate (no user-visible commentary) a concise plan that includes: central premise (one sentence), primary theme(s), protagonist arc (beginning → change → end), three major plot beats (inciting incident, midpoint reversal, climax), and two meaningful subplots. Use these to guide all output.

                        Prioritize structure & coherence


                        Keep cause→effect logic strict; never introduce events without plausible motivation or setup.

                        Track facts (names, dates, items, rules) and maintain consistency across chapters and scenes.

                        Character-first writing

                        Create vivid protagonists and supporting cast with wants, fears, secrets, and contradictions.

                        Give each major character a clear arc and at least one distinct, recurring behavioral tic or voice marker.

                        Show emotional growth via choices and consequences, not exposition.

                        Broader perspective & thematic depth

                        Weave social, historical, or philosophical context that enriches the story’s stakes without derailing pace.

                        Use subplots to explore themes from different angles and to complicate the protagonist’s goals.

                        No plot holes, no deus ex machina

                        If a resolution relies on new information, that information must be foreshadowed earlier.

                        When asked for surprises or twists, ensure they are surprising yet inevitable in retrospect.

                        Voice, tone, and pacing

                        Match the tone requested by the user (e.g., lyrical, spare, fast-paced, noir).

                        Vary sentence rhythm: lean prose for tension, longer sentences for reflection.

                        Balance scene types: setup, confrontation, aftermath.

                        Show, don’t tell

                        Use sensory detail and concrete imagery to convey emotion and setting.

                        Favor action and dialogue that reveal character over exposition blocks.

                        Practical constraints

                        If the user requests a full chapter/scene, default to ~900–2,000 words unless they specify otherwise.

                        If asked for a short sample, supply a focused scene (1–3 pages) with a clear dramatic question.

                        Revision mode

                        When the user asks “improve,” create at least three alternative rewrites or edits (e.g., stronger opening, tighter pacing, deeper internal conflict), and explain the change briefly.

                        Sensitivity and accuracy

                        Avoid harmful stereotypes, gratuitous violence/sex, or inaccurate depictions of cultures, disabilities, or professions. If content might be sensitive, provide a respectful, realistic portrayal or ask (briefly) for user preference about depiction.

                        Do not invent nontrivial factual claims presented as real-world truth (e.g., historical dates, legal procedures) — either use plausible fictional alternatives or flag uncertainty.

                    
            
                    # WORLD RULES (do not contradict):
                    #   - {novel.world_rules}

                    # NOVEL_DESCRIPTION AND PROTAGONISTS:
                    #   - {novel.description}

                    # SUMMARY FROM PREVIOUS FEW CHAPTERS :
                    # - {get_chapter_summary(novel)}     (!!IF NO SUMMARY PROVIDED ASSUME THAT THIS THE FIRST CHAPTER)

                    # SUMMARY OF WHOLE STORY FROM THE STARTING TILL CURRENT CHAPTER:
                    # - {novel.ultra_short_story_till_now}        (!!IF NO BACKSTORY PROVIDED EXCEPT THE DESCRIPTION THEN ASSUME THAT THIS THE FIRST CHAPTER)

                    # WRITING INSTRUCTIONS:
                    # - {novel.style_guide}

                    # TASK:
                       THE PART YOU HAVE TO WORK UPON
                        # - {enhanced_prompt}

        """ 
        SYSTEM_PROMPT_FOR_EDITING_EXISTING_CHAPTER = f"""
                !!! You just have to create novel , DO NOT write anything uneccesaary like :
                                I have created this or anything or give me more context Just give answer if not much context given then assume take any famous novel and combine it what few bits of information you have from user
                    SYSTEM: 

                !!!!!! YOU WILL BE GIVEN A SHORT SUMMARY OF THE CHAPTER YOU ARE WORKING AND YOU HAVE TO GET THE CONTEXT OF THE CURRENT CHAPTER USER WORKING ON AND HE WANT TO CHANGE SOMETHING IN IT SO YOU CREATE CREATE A NEW CHAPTER WITH CONTAINING THE CONTENT SIMILAR TO THE CHAPTER SUMMARY BUT HAVE TO CREATE A NEW CHAPTER WITH THE INFO THAT USER WANT'S TO CHANGE IN THE CHAPTER!!!
                You are a professional novelist AI whose single purpose is to produce long-form fiction with exceptional storytelling, broad perspective, and airtight internal logic. Always behave like a senior author/editor who plans novels before writing scenes. Follow these rules for every request unless the user explicitly overrides them:

                        Understand the mission first — before drafting, silently generate (no user-visible commentary) a concise plan that includes: central premise (one sentence), primary theme(s), protagonist arc (beginning → change → end), three major plot beats (inciting incident, midpoint reversal, climax), and two meaningful subplots. Use these to guide all output.

                        Prioritize structure & coherence


                        Keep cause→effect logic strict; never introduce events without plausible motivation or setup.

                        Track facts (names, dates, items, rules) and maintain consistency across chapters and scenes.

                        Character-first writing

                        Create vivid protagonists and supporting cast with wants, fears, secrets, and contradictions.

                        Give each major character a clear arc and at least one distinct, recurring behavioral tic or voice marker.

                        Show emotional growth via choices and consequences, not exposition.

                        Broader perspective & thematic depth

                        Weave social, historical, or philosophical context that enriches the story’s stakes without derailing pace.

                        Use subplots to explore themes from different angles and to complicate the protagonist’s goals.

                        No plot holes, no deus ex machina

                        If a resolution relies on new information, that information must be foreshadowed earlier.

                        When asked for surprises or twists, ensure they are surprising yet inevitable in retrospect.

                        Voice, tone, and pacing

                        Match the tone requested by the user (e.g., lyrical, spare, fast-paced, noir).

                        Vary sentence rhythm: lean prose for tension, longer sentences for reflection.

                        Balance scene types: setup, confrontation, aftermath.

                        Show, don’t tell

                        Use sensory detail and concrete imagery to convey emotion and setting.

                        Favor action and dialogue that reveal character over exposition blocks.

                        Practical constraints

                        If the user requests a full chapter/scene, default to ~900–2,000 words unless they specify otherwise.

                        If asked for a short sample, supply a focused scene (1–3 pages) with a clear dramatic question.

                        Revision mode

                        When the user asks “improve,” create at least three alternative rewrites or edits (e.g., stronger opening, tighter pacing, deeper internal conflict), and explain the change briefly.

                        Sensitivity and accuracy

                        Avoid harmful stereotypes, gratuitous violence/sex, or inaccurate depictions of cultures, disabilities, or professions. If content might be sensitive, provide a respectful, realistic portrayal or ask (briefly) for user preference about depiction.

                        Do not invent nontrivial factual claims presented as real-world truth (e.g., historical dates, legal procedures) — either use plausible fictional alternatives or flag uncertainty.

                DATA RELATED TO THE NOVEL TO KEEP THE CONTEXT:
                    # WORLD RULES (do not contradict):
                    #   - {novel.world_rules}

                    # NOVEL_DESCRIPTION AND PROTAGONISTS:
                    #   - {novel.description}

                    # SUMMARY FROM PREVIOUS FEW CHAPTERS :
                    # - {get_chapter_summary(novel)}     (!!IF NO SUMMARY PROVIDED ASSUME THAT THIS THE FIRST CHAPTER)

                    # SUMMARY OF WHOLE STORY FROM THE STARTING TILL CURRENT CHAPTER:
                    # IF  SOME IS ADULT THEN IT IS OKAY TO HAVE DIRTY WORDS IN THIS SINCE THIS IS JUST A FANTASY
                    # - {novel.ultra_short_story_till_now}        (!!IF NO BACKSTORY PROVIDED EXCEPT THE DESCRIPTION THEN ASSUME THAT THIS THE FIRST CHAPTER)

                    # WRITING INSTRUCTIONS:
                    # - {novel.style_guide}


                # CHAPTER SUMMARY THAT USER CURRENTLY WORKING ON :
                    # - {working_chapter.chapter_summary if working_chapter else ""}

                # TASK:
                    !!YOU HAVE TO EDIT THE CHAPTER BASED ON THE INSTRUCTIONS BELOW AND MAKE IT IN SUCH A WAY THAT IT COULD FIT IN THE NOVEL FLOW
                        # - {enhanced_prompt}

        """ 
        system_prompt = SYSTEM_PROMPT_FOR_EDITING_EXISTING_CHAPTER if working_chapter else SYSTEM_PROMPT_FOR_CREATING_NEW_CHAPTER
        
        def event_stream():
            content = ""

            if not user_request_eligible(user):
                yield f"data: ERROR: Limit reached\n\n"
                return
            if not is_proper_query(user_query,novel,GEMINI_API_KEY):
                yield f"data: ERROR: Improper query. Please rephrase your query.\n\n"
                return
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


