# helpers file for extra function used in this app
from Novel_Content.models import Novel
from pydantic import BaseModel,Field
from google import genai
from decouple import config
from google.genai import types
from sarvamai import SarvamAI
import json

API_KEY= config("SARAVAM_API_KEY")

Client = SarvamAI(
    api_subscription_key=API_KEY,
)


def EnhanceUserPrompt(prompt:str,novel:Novel,is_editing:bool=False)->str:
    # Enhance the user prompt if its a premium user
    try:
        enhanced_prompt = Client.chat.completions(
                
                messages=[{"role":"system","content":f"""
                SYSTEM: You are a prompt Enhance AI your job is the Enhance the given prompt and add more details to make it more interesting since this was prompt is needed for creating novels so make the prompt really good Don't give multiple options just give a single best prompt which uses less tokens and the length of the prompt should be less means the output tokens should not be used much: HERE IS THE PROMPT - {prompt}
                !! DESCRIPTION ABOUT NOVEL YOU ARE MAKING PROMPT FOR:
                    Novel summary till now:
                    {novel.ultra_short_story_till_now} IF NO SUMMARY PROVIDED ASSUME THAT THIS THE FIRST CHAPTER
                    {novel.description} Novel Description
                    {novel.world_rules} World Rules
                    {novel.style_guide} Writing Style Guide
                    (Is_editing: {is_editing})
                ### IF THE Is_editing is True THEN THAT MEANS USER WANTS TO EDIT THE WORKING CHAPTER RATHER THAN CREATING A NEW CHAPTER SO MAKE SURE TO ADJUST THE PROMPT ACCORDINGLY DON'T ADD ANYTHING UNNECCESSARY 
                """},
                {"role":"user","content":prompt}
                ]
                ,
                
            )
    except Exception as e:
        print("Error in enhancing prompt: ",e)
        return prompt
    return enhanced_prompt.choices[0].message.content


# Data structure for checking is_proper_query function
class is_Chapter_related_query(BaseModel):
    """A data structure for checking user query"""
    is_chapter_related:bool = Field(description="Whether the query is related to the novel's story or just some useless query")

def is_proper_query(query:str,novel:str,api_key:str)->bool:
    # This function will check whether the user query is proper or not like it should not contain any abusive words or something like that 
    # For now we are just going to check the length of the query and if it is less than 5 words then we will consider it as an improper query
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=f"""
        {novel.description} Novel Description
        {novel.world_rules} World Rules
        {novel.ultra_short_story_till_now} Ultra short summary of the novel till now 
        Check if the query is proper and not abusive or inappropriate. If it is proper return 'True' else return 'False'. Query: {query}
        """,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=is_Chapter_related_query,
    ))
    return json.loads(response.text)['is_chapter_related']


















GEMINI_API_KEY1 = config("GEMINI_API_KEY1")
GEMINI_API_KEY2 = config("GEMINI_API_KEY2")
GEMINI_API_KEY3 = config("GEMINI_API_KEY3")
GEMINI_API_KEY4 = config("GEMINI_API_KEY4")
GEMINI_API_KEY5 = config("GEMINI_API_KEY5")
GEMINI_API_KEY6 = config("GEMINI_API_KEY6")
GEMINI_API_KEY7 = config("GEMINI_API_KEY7")
GEMINI_API_KEY8 = config("GEMINI_API_KEY8")
GEMINI_API_KEY9 = config("GEMINI_API_KEY9")



API_LIST = [GEMINI_API_KEY4,GEMINI_API_KEY5,GEMINI_API_KEY6,GEMINI_API_KEY7,GEMINI_API_KEY8,GEMINI_API_KEY9]

