"""
        File containing Structure for different AI response 
"""
from pydantic import BaseModel,Field


# Data structure for extra chapter content 
class Content_and_Summary(BaseModel):
    """A data structure for storing content and its summary."""
    chapter_name:str = Field(description="based on the summary give the chapter a suitable name ")
    summary: str = Field(description="Just give the main points so that you could understand these later or even some keyword for you to understand as you have to read these later without reaching the context window limit")
    ultra_short_summary:str = Field(description="this is the ultra short summary that will be stored for keeping the context of the full story")


# Data structure for checking is_proper_query function
class is_Chapter_related_query(BaseModel):
    """A data structure for checking user query"""
    is_chapter_related:bool = Field(description="Whether the query is related to the novel's story or just some useless query")
    reason:str = Field(description="If the query is not related to the story then give the reason why it is not related or why it is abusive or inappropriate")
