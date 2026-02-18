# helpers file for extra function used in this app

from google import genai
from decouple import config

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



def EnhanceUserPrompt(prompt:str,novel:str,api_key:str,is_editing:bool=False)->str:

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
                ### IF THE Is_editing is True THEN THAT MEANS USER WANTS TO EDIT THE WORKING CHAPTER RATHER THAN CREATING A NEW CHAPTER SO MAKE SURE TO ADJUST THE PROMPT ACCORDINGLY DON'T ADD ANYTHING UNNECCESSARY 
                """,
                
            )
    
    return enhanced_prompt.text



