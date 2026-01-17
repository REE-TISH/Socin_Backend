from Novel_Content.models import Genre,Tag


def is_Premium(user):
    return user.groups.filter(name="premium_plan").exists()

def get_genre_id_list(genre_list):
    arr = []
    for g in genre_list:
        genre_id = Genre.objects.get(name=g).id
        arr.append(genre_id)
    return arr

def get_tag_id_list(tags_list):
    arr = []
    for t in tags_list:
        tag_id = Tag.objects.get(name=t)
        arr.append(tag_id.id)
    return arr
