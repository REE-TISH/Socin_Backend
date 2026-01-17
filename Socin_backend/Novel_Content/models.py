from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class Genre(models.Model): # Tells what kind of story is (Horror , Action etc)
    name = models.CharField(max_length=120,unique=True)

    def __str__(self):
        return self.name
    
class Tag(models.Model):        # Give little bit context about the story
    name = models.CharField(max_length=120,unique=True) 

    def __str__(self):
        return self.name

class Novel(models.Model):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="created_by")
    created_at = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)
    genres = models.ManyToManyField(Genre)
    tags = models.ManyToManyField(Tag)
    # novel_image = models.ImageField(upload_to="novel_images/",blank=True,) # Cover Image of the Novel
    novel_image = models.URLField(blank=True)
    likes = models.IntegerField(default=0) # No. of likes Novel has
    views = models.IntegerField(default=0) # No. of Views Novel has 
    world_rules = models.TextField(blank=True) # Fundamental rules for the world in which the story is set or other fundamental things
    current_chapter = models.PositiveIntegerField(default=0)
    ultra_short_story_till_now = models.TextField(blank=True) # To keep the context of whole story
    isPublic = models.BooleanField(default=True) 
    popularity_score = models.FloatField(default=0)
    style_guide = models.TextField(
        help_text="POV, tense, prose style, tone rules",blank=True) 


    def __str__(self):
        return f"{self.name} by - {self.created_by}"  

ACTION_CHOICES = [
        ("like", "Like"),
        ("bookmark", "Bookmark"),
    ]

class UserLikes_Bookmarks(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    novel = models.ForeignKey(Novel,on_delete=models.CASCADE)
    action = models.CharField(max_length=30,choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

class Chapter(models.Model):
    related_novel = models.ForeignKey(Novel,on_delete=models.CASCADE,related_name="novel_chapter")
    name = models.CharField(max_length=200,blank=True)
    chapter_no = models.PositiveIntegerField(blank=True)
    content = models.TextField(blank=True)
    chapter_summary = models.TextField(default='')

    class Meta:
        ordering = ["related_novel","chapter_no",]

    def __str__(self):
        return f"{self.related_novel.name} :- chapter_no {self.chapter_no} '{self.name}'"
    

#*  To get the context from previous three chapters:
def get_chapter_summary(novel):
    all_chapters = Chapter.objects.filter(related_novel=novel)
    chapter_summary = ''
    chapters_count = len(chapter_summary)
    if chapters_count > 3: # If the number of chapter is more than 3 then get the last three chapters summary
        for chapter in all_chapters[chapters_count-4:chapter_summary]:  
            chapter_summary = chapter_summary + chapter.chapter_summary 
    else:
        for chapter in all_chapters: # number of chapter 3 or less then retrieve all the summary from these chapters
            chapter_summary =  chapter_summary + chapter.chapter_summary 
    return chapter_summary









