""" Helper Functions Related To User Daily Usage """
import re
from django.contrib.auth import get_user_model

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

def get_user_id(username):
    return f"@{username}{uuid.uuid4()}"


def generate_unique_user_id(base_name: str) -> str:
    """
    Generates a user_id
    """

    # 1. Normalize (instagram rules)
    base_name = base_name.lower()
    base_name = re.sub(r'[^a-z0-9._]', '', base_name)
    base_name = base_name.strip("._")

    if not base_name:
        base_name = "user"

    # 2. If base name is free → return it
    if not User.objects.filter(user_id=base_name).exists():
        return base_name

    # 3. Otherwise append numbers
    counter = 1
    while True:
        new_user_id = f"{base_name}_{counter}"
        if not User.objects.filter(user_id=new_user_id).exists():
            return new_user_id
        counter += 1