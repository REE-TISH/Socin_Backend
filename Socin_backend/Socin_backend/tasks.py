# from celery import shared_task
# from AI_Content_Generation.novel_creation import Create_Story_Of_Novel_Chapter
# from Novel_Content.models import Chapter
# from Novel_Content.models import get_chapter_summary

# @shared_task
# def get_AI_Response(NovelDescription='',Writing_style='',WorldRules='',User_Query='',chapter_id=''):
#         PreviousChapters,novel = get_chapter_summary(chapter_id)
#         response = Create_Story_Of_Novel_Chapter(NovelDescription,Writing_style,PreviousChapters,novel.ultra_short_story_till_now,WorldRules,User_Query)
#         chapter = Chapter.objects.get(id=chapter_id)
#         chapter.content = response['content']
#         chapter.chapter_summary = response['summary']
#         chapter.name = response['chapter_name']
#         chapter.save()
#         novel.ultra_short_story_till_now = novel.ultra_short_story_till_now + response['ultra_short_summary']
#         novel.save()

