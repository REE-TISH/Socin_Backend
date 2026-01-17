from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from decouple import config
from django.conf import settings
from .helpers import generate_unique_user_id
from .serializers import CustomUserCreation_Serializer,UserProfileData_Serializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password


User = get_user_model()

# For direct login through GOOGLE ACCOUNT without setting any password
class GoogleAuthView(APIView):
    def post(self, request):
        token = request.data.get("token")
      
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                config("CLIENT_ID")
            )
            avatar = idinfo.get("picture", "")
            email = idinfo["email"]
            name = idinfo.get("name", "")
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"user_id":generate_unique_user_id(name),"username": name, }
            )
            if created:
                user.avatar = avatar
                user.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })

        except ValueError:
            return Response({"error": "Invalid token"}, status=400)


# VIEW FOR CREATING USER
class Create_User_API_VIEW(APIView):
    
    def post(self,request):
        data = request.data
        serializer = CustomUserCreation_Serializer(data=data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({"response":"User was created successfully"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_417_EXPECTATION_FAILED)


# API View TO GET PROFILE DATA
@api_view(['GET'])
@permission_classes([IsAuthenticated])          # User should be authenticated
def get_your_profile_data_API_VIEW(request,*args,**kwargs):
    user = request.user
    serializer = UserProfileData_Serializer(user)
    return Response(serializer.data,status=status.HTTP_200_OK)


# Api VIEW TO EDIT USER PROFILE
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_user_info_api(request):
    user = request.user
    data = request.data
    if (list(data.keys()) != ['name', 'bio']):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        user.username = data['username']
        user.bio = data['bio']
        user.save() 
    except:
        return Response({'error':'data provided not correct'},status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_201_CREATED)


# SET PASSWORD OR CHANGE PASSWORD API VIEW
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password_API_VIEW(request):
    user = request.user
    data = request.data
    if not user.password: # IF NO PASSWORD HAS BEEN SET THEN 
        user.set_password(data['old_password'])
        user.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    if not check_password(data['old_password'],user.password): # If password doesn't match then return ERR
        return Response({"data":"password doesn't match"},status=status.HTTP_406_NOT_ACCEPTABLE)
    user.set_password(data['new_password'])
    user.save()
    return Response(status=status.HTTP_202_ACCEPTED)
    
# DELETE ACCOUNT API VIEW
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account_API_VIEW(request):
    user = request.user
    user.delete()
    return Response(status=status.HTTP_200_OK)