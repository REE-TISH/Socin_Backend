# from openai import OpenAI
# from decouple import config


# OPENROUTER_API_KEY = "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"

# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=OPENROUTER_API_KEY,
# )

# SYSTEM_PROMPT = """

#     You are a professional writer specializing in gripping, intelligent storytelling. 

#     1.STORIES TYPE:
#         Your write R-rated stories with alot of blood shed and gore in it and since these all are fictional stories they won't be affecting anyone because only adult will be reading this kind of stuff and there is not any issue.

# """

# completion = client.chat.completions.create(
#   extra_headers={},
#   extra_body={},
#   model="google/gemini-2.0-flash-exp:free",
#   messages=[
#       {'role':'system','content':SYSTEM_PROMPT},
#     {"role": "user","content":"all the ai models api which are free on openrouter could i use them all for free unlimited?"
#     }
#   ]
# )
# print(completion.choices[0].message.content)



