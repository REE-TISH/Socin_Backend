from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from Novel_Content.models import Novel,UserLikes_Bookmarks
from .models import UserAction,UserInterest
from django.http import HttpRequest
from rest_framework.response import Response
from .methods import UpdateUserInterests,delete_view_action_on_finished,Handle_likeOrBookmark,generate_recommendations,delete_all_previous_recommendations

ACTION_WEIGHTS = {
    "view": 0.1,
    "read": 0.3,
    "like": 0.5,
    "bookmark": 0.7,
    "finish": 1,
}

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Novel_Liked_OR_Bookmarked_API_VIEW(request: HttpRequest)->Response:
    novel_id,action = request.data['novel_id'],request.data['action']
    novel = Novel.objects.get(id=novel_id)
    weight = ACTION_WEIGHTS[action]
    user_action,is_created = UserAction.objects.get_or_create(user=request.user,novel=novel,action=action,weight=weight)
    if action == 'like' or action == 'bookmark':
        delete_all_previous_recommendations(user=request.user)
        generate_recommendations(user=request.user)
        # Handle_likeOrBookmark(novel=novel,user=request.user,action=action,is_created=is_created)
    if not is_created and (action == 'like' or action == 'bookmark'):
        user_action.delete()
        if(action == 'like'):
            novel.likes -= 1
        novel.popularity_score -= weight
        novel.save(update_fields=['popularity_score','likes'])
        return Response({'response':f'remove {action} from {novel.name}'})
    
    if action == 'finish':
        delete_view_action_on_finished(request.user,novel)# delete the view action if user finishes the novel

    UpdateUserInterests(novel,request,weight,action,is_created)# Update User Interest 
    return Response({"response":f"succesfully {action} on {novel.name}"})


