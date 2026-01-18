""" Helper Functions Related To User Daily Usage """
import re
from django.contrib.auth import get_user_model
#  cloudinary imports
import cloudinary
from decouple import config
import cloudinary.uploader
User = get_user_model()

def could_user_make_request(user):
    if user.is_premium and user.daily_usage.chapter_creation_requests_made < 20:
        return True  # Premium users can make 20 requests per day
    elif not user.is_premium and user.daily_usage.chapter_creation_requests_made < 5:
        return True  # Free users can make 5 requests per day
    else:
        return False  # User has exceeded their daily request limit
    
def increment_user_request_count(user):
    user.daily_usage.chapter_creation_requests_made += 1
    user.daily_usage.save(update_fields=["chapter_creation_requests_made"])


def user_request_eligible(user):
    user.daily_usage.reset_if_needed()
    return could_user_make_request(user)


def generate_unique_user_id(base_name: str) -> str:
    """
    Generates a user_id
    """

   
    base_name = base_name.lower()
    base_name = re.sub(r'[^a-z0-9._]', '', base_name)
    base_name = base_name.strip("._")

    if not base_name:
        base_name = "user"

    # If base name is free → return it
    if not User.objects.filter(user_id=base_name).exists():
        return base_name

    # Otherwise append numbers
    counter = 1
    while True:
        new_user_id = f"{base_name}_{counter}"
        if not User.objects.filter(user_id=new_user_id).exists():
            return new_user_id
        counter += 1


def get_public_id_from_url(url):
    """
    Extracts the public_id from a Cloudinary image URL.
    """
    # Regex to match the path after 'upload/' and capture the public_id before the extension
    if not url:
        return
    match = re.search(r'/upload/(?:v\d+/)?([^.]+)(?:\.\w{3,4})?$', url)
    if match:
        return match.group(1)
    return None

  # Contains cloudinary Config
cloudinary.config( 
    cloud_name = config("CLOUD_NAME"), 
    api_key = config("CLOUD_API_KEY"), 
    api_secret = config("CLOUD_SECRET_KEY") 
)

def delete_image_by_url(public_id):
    try:
        # Delete the asset
        result = cloudinary.uploader.destroy(
            public_id,
            invalidate=True  # Invalidate cached copies on the CDN
        )
        print(f"Deletion result for {public_id}: {result}")
    except Exception as e:
        print(f"An error occurred during deletion: {e}")


