"""
Contains cloudinary Config
"""
import cloudinary
from decouple import config
import cloudinary.uploader

cloudinary.config( 
    cloud_name = config("CLOUD_NAME"), 
    api_key = config("CLOUD_API_KEY"), 
    api_secret = config("CLOUD_SECRET_KEY") 
)