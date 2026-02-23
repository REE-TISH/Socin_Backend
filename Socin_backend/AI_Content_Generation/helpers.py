# helpers file for extra function used in this app
from openai import api_key

from Novel_Content.models import Novel
from .models import ChapterBeingCreated
from pydantic import BaseModel,Field
from Custom_user.helpers import increment_user_request_count
from .AI_structured_response import Content_and_Summary , is_Chapter_related_query
from google import genai
from decouple import config
from google.genai import types
from sarvamai import SarvamAI
import json

API_KEY= config("SARVAM_API")

Client = SarvamAI(
    api_subscription_key=API_KEY,
)

def EnhanceUserPrompt(prompt:str,api_key:str,novel:Novel,working_chapter,is_editing:bool=False)->str:
    # Enhance the user prompt if its a premium user
    try:
        #------------------SARVAM AI ENHANCEMENT------------------    
        # enhanced_prompt = Client.chat.completions(
                
        #         messages=[{"role":"system","content":f"""
        #         SYSTEM: You are a prompt Enhance AI your job is the Enhance the given prompt and add more details to make it more interesting since this was prompt is needed for creating novels so make the prompt really good Don't give multiple options just give a single best prompt which uses less tokens and the length of the prompt should be less means the output tokens should not be used much: HERE IS THE PROMPT - {prompt}
        #         !! DESCRIPTION ABOUT NOVEL YOU ARE MAKING PROMPT FOR:
        #             Novel summary till now:
        #             {novel.ultra_short_story_till_now} IF NO SUMMARY PROVIDED ASSUME THAT THIS THE FIRST CHAPTER
        #             {novel.description} Novel Description
        #             {novel.world_rules} World Rules
        #             {novel.style_guide} Writing Style Guide
        #             (Is_editing: {is_editing})
        #         ### IF THE Is_editing is True then you have to make the prompt based the fact that user is working on the chapter with the following content and user want to make some changes in that chapter so you have to make the prompt in such a way that it could help in making changes in that chapter content and also you have to keep in mind that the user want to make some reasonable changes in that chapter content and you have to make the prompt accordingly :
        #             Chapter content that user is working on :
        #                 {working_chapter if working_chapter else ""}
        #         """},
        #         {"role":"user","content":prompt}
        #         ]
        #         ,
                
        #     )
        # ------------------------------------------------------------

            client = genai.Client(api_key=api_key)
            enhanced_prompt = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=f"""
                     SYSTEM: You are a prompt Enhance AI your job is the Enhance the given prompt and add more details to make it more interesting since this was prompt is needed for creating novels so make the prompt really good Don't give multiple options just give a single best prompt which uses less tokens and the length of the prompt should be less means the output tokens should not be used much: HERE IS THE PROMPT - {prompt}
                !! DESCRIPTION ABOUT NOVEL YOU ARE MAKING PROMPT FOR:
                    Novel summary till now:
                    {novel.ultra_short_story_till_now} IF NO SUMMARY PROVIDED ASSUME THAT THIS THE FIRST CHAPTER
                    {novel.description} Novel Description
                    {novel.world_rules} World Rules
                    {novel.style_guide} Writing Style Guide
                    (Is_editing: {is_editing})
                ### IF THE Is_editing is True then you have to make the prompt based the fact that user is working on the chapter with the following content and user want to make some changes in that chapter so you have to make the prompt in such a way that it could help in making changes in that chapter content and also you have to keep in mind that the user want to make some reasonable changes in that chapter content and you have to make the prompt accordingly :
                    Chapter content that user is working on :
                        {working_chapter if working_chapter else ""}    
                    """)
            return enhanced_prompt.text
    except Exception as e:
        print("Error in enhancing prompt: ",e)
        return prompt
    

#? Summarize and provide chapter name AND STORING the chapter to the ChapterBeingCreated model
def Summarize_Chapter_Content(chapter_content:str,api_key:str,novel:Novel,user)->bool:
    client = genai.Client(api_key=api_key)
    if not chapter_content or len(chapter_content)<100:
        """Chapter content is too short to summarize"""
        print("Chapter content is too short to summarize")
        return False
    try:
        chapter_summarization = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=f"SYSTEM: You are an AI novel summarizer expert , Your job is to summarize the given content in as small context as possible with keeping the meaning of that novel chapter so that it could be used for the creation of furthur chapters . HERE IS THE NOVEL CHAPTER THAT YOU HAVE TO WORK UPON: {chapter_content}",
                config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=Content_and_Summary,
                )
            )
        dictionary_chapter_content = json.loads(chapter_summarization.text)
        print("####CHAPTER SUMMARY AND NAME",dictionary_chapter_content)
        increment_user_request_count(user)
        # Save the Current Chapter User working on in DB
        ChapterBeingCreated.objects.get_or_create(
            user=user,
            novel=novel,
            content=chapter_content,
            chapter_name=dictionary_chapter_content['chapter_name'],
            chapter_summary=dictionary_chapter_content['summary'],
            ultra_short_summary=dictionary_chapter_content['ultra_short_summary'],
        )
    except Exception as e:
        print("!!!Error in saving and summarizing chapter")
        return False
    return True
        
    

#? Checking proper prompt
def is_proper_query(query:str,api_key:str,working_chapter_content:str,is_editing:bool=False)->bool:
    
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=f"""
        Check if the query is proper and not inappropriate. If it is proper return 'True' else return 'False'. Query: {query}
        For example:
            query: "Can you write a chapter where the main character goes to the moon?"
            response: "Sorry the main character can't go beyond the earth because the novel is based on real world and it doesn't have any sci-fi element so this query is not related to the story and also it is not proper because it is asking for something that is not related to the story and also it is asking for something that is not possible in the real world response will be False"

            query:"write the next chapter"
            response:"This query is proper because it is related to the story and it is asking for something that is possible in the novel world so this query is related to the story and also it is proper because it is asking for something that is related to the story and also it is asking for something that is possible in the novel world response will be True"

            !!VERY VERY VERY IMPORTANT :
                is_editing_status:{is_editing}
                "is_editing_status is True then return True in response for the similar example"
                        Example for editing True:
                            query:change the language to SOME_LANGUAGE (changing language or similar)
                            response:True

                            query:(QUERY GIVEN TO MAKE A REASONABLE CHANGE SOMETHING IN THE WORKING CHAPTER 
                                working chapter_content Chapter content:{working_chapter_content if is_editing else ""})
                            response:True
                 
                
        """,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=is_Chapter_related_query,
    ))
    print(response.text)
    return json.loads(response.text)


















GEMINI_API_KEY1 = config("GEMINI_API_KEY1")
GEMINI_API_KEY2 = config("GEMINI_API_KEY2")
GEMINI_API_KEY3 = config("GEMINI_API_KEY3")
GEMINI_API_KEY4 = config("GEMINI_API_KEY4")
GEMINI_API_KEY5 = config("GEMINI_API_KEY5")
GEMINI_API_KEY6 = config("GEMINI_API_KEY6")
GEMINI_API_KEY7 = config("GEMINI_API_KEY7")
GEMINI_API_KEY8 = config("GEMINI_API_KEY8")
GEMINI_API_KEY9 = config("GEMINI_API_KEY9")



API_LIST = [GEMINI_API_KEY1,GEMINI_API_KEY2,GEMINI_API_KEY3,GEMINI_API_KEY4,GEMINI_API_KEY5,GEMINI_API_KEY6,GEMINI_API_KEY7,GEMINI_API_KEY8,GEMINI_API_KEY9]

