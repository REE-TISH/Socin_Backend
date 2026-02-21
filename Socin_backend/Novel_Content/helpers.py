from Novel_Content.models import Genre,Tag
from typing import List

def is_Premium(user)->bool:
    return user.groups.filter(name="premium_plan").exists()

def get_genre_id_list(genre_list:List[str])->List[int]:
    arr:List[int] = []
    for g in genre_list:
        genre_id = Genre.objects.get(name=g).id
        arr.append(genre_id)
    return arr

def get_tag_id_list(tags_list:List[str])->List[int]:
    arr:List[int] = []
    for t in tags_list:
        tag_id = Tag.objects.get(name=t)
        arr.append(tag_id.id)
    return arr
