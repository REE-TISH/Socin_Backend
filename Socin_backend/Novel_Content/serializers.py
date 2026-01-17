from rest_framework import serializers
from .models import Novel,Chapter,Tag,Genre
from django.contrib.auth import get_user_model
from RecommendationSystem.models import UserAction

# User 
User = get_user_model()

# Genre Serializer For putting data
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id','name']


# To serialize a single novel data and send it to the user 
class Novel_Serializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    chapter_count = serializers.SerializerMethodField(read_only=True)
    author_avatar = serializers.URLField(source='created_by.avatar',read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_bookmarked = serializers.SerializerMethodField(read_only=True)
    genres = GenreSerializer(many=True)

    class Meta:
        model = Novel
        fields = ['id','name','author','description','genres','novel_image','chapter_count','isPublic','author_avatar','is_liked','likes','views','is_bookmarked']
    
    def get_author(self,obj):
        return obj.created_by.username
    
    def get_chapter_count(self,obj):
        return obj.novel_chapter.all().count()
    
    def get_is_liked(self,obj):
        user = self.context['request'].user
        is_liked = UserAction.objects.filter(user=user,novel=obj,action='like').exists()
        return is_liked
    def get_is_bookmarked(self,obj):
        user = self.context['request'].user
        is_bookmarked = UserAction.objects.filter(user=user,novel=obj,action='bookmark').exists()
        return is_bookmarked    

# To serialize all the novels data for showing all the novels available
class Novels_Serializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Novel
        fields = ['id','name','author','novel_image','genres']

    def get_author(self,obj):
        return obj.created_by.username
    

# For creating novels containing further details like world rules & styles_guide etc
class Novel_Creation_Serializer(serializers.ModelSerializer):

    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset = Tag.objects.all(),many=True
    )

    class Meta:
        model = Novel
        fields = '__all__'

    
    def create(self, validated_data):
        genres = validated_data.pop('genres', [])
        tags = validated_data.pop('tags', [])

        novel = Novel.objects.create(**validated_data)
        novel.genres.set(genres)
        novel.tags.set(tags)

        return novel

class Chapter_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id','name','chapter_no','content']

class Chapter_creation_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id','name','related_novel','chapter_no','content','chapter_summary']
