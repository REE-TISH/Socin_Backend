from AI_Content_Generation.models import ChapterBeingCreated
from .serializers import (
    Novel_Serializer,
    Novels_Serializer,
    Novel_Creation_Serializer,
    Chapter_creation_Serializer,
    )
from django.http import HttpRequest
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics,status
from rest_framework.views import APIView
from .models import Novel,Chapter
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from RecommendationSystem.methods import generate_recommendations
from django.db.models import Case, When
from .helpers import get_genre_id_list,get_tag_id_list,is_Premium
# Create your views here.


# Create User through API call
User = get_user_model()

# Get all the novels 
class All_Novels_API_VIEW(generics.ListAPIView):
    queryset = Novel.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = Novels_Serializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        novel_ids = generate_recommendations(user)
        if not novel_ids:
            return Novel.objects.filter(isPublic=True).order_by('-popularity_score')  
        preserved_order = Case(
        *[When(id=pk, then=pos) for pos, pk in enumerate(novel_ids)]
        )

        return Novel.objects.filter(
            id__in=novel_ids,
            isPublic=True
        ).order_by(preserved_order)

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['status'] = 'success'
        response.data['extra_data'] = {
            'is_premium':self.request.user.is_premium,
            'avatar':self.request.user.avatar
        }
        return response



# For Novel Detail page
class Get_Novel_Data_API_VIEW(generics.RetrieveAPIView):
    queryset = Novel.objects.all()
    serializer_class = Novel_Serializer
    lookup_field = 'pk'


# Get the Chapter that User wants to read From given_id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getNovelChapter_API_VIEW(request:HttpRequest,*args,**kwargs)->Response:
    chapter_no = kwargs['pk']  # Chapter no
    novel_id = kwargs['novel_id']
    related_novel = get_object_or_404(Novel,id=int(novel_id)) # Finds the novel through novel id

    chapter = get_object_or_404(Chapter,chapter_no=chapter_no,related_novel=related_novel) 
    return Response({"novel":chapter.related_novel.name,
                    "chapter_name":chapter.name,  # return the chapter which the user wants to read from the chosen novel
                    "chapter_no":chapter_no,
                    "content":chapter.content,}) 



# Users personal created novels
class Personal_Novels_API_VIEW(generics.ListAPIView):
    queryset = Novel.objects.all()
    serializer_class = Novel_Serializer

    def get_queryset(self):
        user = self.request.user
        personal_novels = Novel.objects.filter(created_by = user) # Return all the personal
        return personal_novels
    
# Create Your Novel
class Create_Novel_API_VIEW(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request:HttpRequest)->Response:
        data = request.data
        user = request.user
        novel_count = Novel.objects.filter(created_by=user).count()
        if not is_Premium(user) and novel_count >= 3:
            return Response({"error":"can't create more novels have to get premium"})
        data['created_by'] = user.id
        # print(data['genres'])
        genre_ids = get_genre_id_list(data['genres'])

        tag_ids = get_tag_id_list(data['tags'])
        print(genre_ids,tag_ids)
        data['tags'] = tag_ids
        data['genres'] = genre_ids
        serializer = Novel_Creation_Serializer(data=data,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



# Create chapter 
#! If You want to use background workers
class Create_Chapter_API_VIEW(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request:HttpRequest,novel_id:str)->Response:

        novel = get_object_or_404(Novel,id=novel_id) 
        user_query = request.data['user_query'] # User prompt
        chapter_number = novel.novel_chapter.all().count() # total number of chapters belong to this novel
        request.data['related_novel'] = novel.id
        
        if request.user != novel.created_by:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        request.data['chapter_no'] = chapter_number + 1  # Set the chapter number
        print(request.data)
        serializer = Chapter_creation_Serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            # get_AI_Response.delay_on_commit(  #* SEND TASK OF CREATING AI RESPONSE TO THE WORKER IN tasks.py 
            #     NovelDescription=novel.description,
            #     Writing_style=novel.style_guide,   
            #     WorldRules=novel.world_rules,
            #     User_Query=user_query,
            #     chapter_id=serializer.data['id'])
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# Finalize the chapter creation and publish it
class Publish_Chapter_API_VIEW(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request:HttpRequest,novel_id:str)->Response:
        novel = get_object_or_404(Novel,id=novel_id) 
        chapter_no = novel.novel_chapter.all().count() # total number of chapters belong to this novel
        if request.user != novel.created_by:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        chapter_User_Working_on = ChapterBeingCreated.objects.filter(user=request.user,novel=novel).order_by('-id').first()
        if not chapter_User_Working_on:
            return Response({"error":"No chapter found that user is working on"},status=status.HTTP_404_NOT_FOUND)
        Chapter.objects.create(
            related_novel = novel,
            name = chapter_User_Working_on.chapter_name,
            chapter_no = chapter_no + 1,
            content = chapter_User_Working_on.content,
            chapter_summary = chapter_User_Working_on.chapter_summary,
        )
        novel.ultra_short_story_till_now += f"\nCHAPTER {chapter_no+1}:{chapter_User_Working_on.ultra_short_summary}"
        novel.save()
        ChapterBeingCreated.objects.filter(novel=novel,user=request.user).delete() # Delete the chapter being created after publishing it
        return Response({"message":"Chapter Published Successfully"},status=status.HTTP_200_OK)

# If the User has chapter that he is working on but hasn't published yet and want to customize the chapter content
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Chapter_User_WorkingOn(request:HttpRequest,novel_id:str)->Response:
    novel = get_object_or_404(Novel,id=novel_id) 
    user = request.user
    if user != novel.created_by: # If the user who sent request is not the same as the creator of the novel
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    chapter_being_created = ChapterBeingCreated.objects.filter(user=user,novel=novel).order_by('-id').first()
    if chapter_being_created:
        
        return Response({
            "chapter_content":chapter_being_created.content,
            "novel_summary":novel.ultra_short_story_till_now,
            "novel":novel.name,
            "working_chapter":novel.novel_chapter.all().count() + 1,
            "message":"You have a chapter being created for this novel"
        },status=status.HTTP_200_OK)
    if not chapter_being_created:
        return Response({
            "chapter_content":None,
            "novel_summary":novel.ultra_short_story_till_now,
            "novel":novel.name,
            "working_chapter":novel.novel_chapter.all().count() + 1,
        },status=status.HTTP_200_OK)                 
    else:
        return Response({
            "message":"No chapter is being created for this novel"
        },status=status.HTTP_404_NOT_FOUND)
    



