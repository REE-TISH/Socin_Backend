from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# User Serializer
User = get_user_model()
class CustomUserCreation_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email','password','avatar','user_id']
        extra_kwargs = {
            'password': {'write_only': True},
            'email':{'required':True},
            'username':{'required':True},
        }
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # Hash password
        user.save()
        return user
    
# User data serializer for profile data
class UserProfileData_Serializer(serializers.ModelSerializer):
    novels_created = serializers.SerializerMethodField(read_only=True)
    is_premium = serializers.SerializerMethodField(read_only=True)
    has_password = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['username','email','bio','novels_created','avatar','is_premium','user_id','created_at','has_password']

    def get_novels_created(self,obj):
        return obj.created_by.all().count()
    
    def get_is_premium(self,obj):
        return obj.groups.filter(name="premium_plan").exists()
    
    def get_has_password(self,obj):
        if not obj.password:
            return False
        return True
    

