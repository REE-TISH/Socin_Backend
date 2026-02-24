from .models import UserInterest,UserAction,UserRecommendations
from Novel_Content.models import Novel,UserLikes_Bookmarks

# Update User interest whenever an Action is done by user
def UpdateUserInterests(novel,request,weight,action,is_created):
    for genre in novel.genres.all(): # Add genre from the novel on which the user has done Action
        obj,_ = UserInterest.objects.get_or_create(
            user=request.user,genre=genre
        )
        obj.score += weight
        obj.save()
    
    for tag in novel.tags.all(): # Add tags from the novel 
        obj,_ = UserInterest.objects.get_or_create(
            user=request.user,tag=tag
        )
        obj.score += weight
        obj.save()       
    if not is_created: # If the user action is not created
        return
    novel.popularity_score += weight
    if action == 'like':
        novel.likes += 1
    if action == 'view':
        novel.views += 1
    novel.save()


def Handle_likeOrBookmark(novel,user,action,is_created):
    if is_created:
        UserLikes_Bookmarks.objects.get_or_create(novel=novel,user=user,action=action)
    if not is_created:
        UserLikes_Bookmarks.objects.delete(novel=novel,user=user,action=action)

# When a user finished the novel the delete the view action of that user
def delete_view_action_on_finished(user,novel):
    view_action = UserAction.objects.filter(user=user,novel=novel,action='view')
    if view_action.exists():
        view_action.delete()

# For creating new recommendations delete all the previous ones
def delete_all_previous_recommendations(user):
    rec = UserRecommendations.objects.filter(user=user)
    if rec:
        rec.delete()

# For generating recommendation based on UserInterest and novel popularity
#!---NOT USING THIS METHOD RIGHT NOW -----(Only recommending novels based on popularity)
def generate_recommendations(user,limit=20):

        if not UserAction.objects.filter(user=user).exists():
            return Novel.objects.filter(isPublic=True).order_by('-popularity_score').values_list('pk',flat=True)
        
        rec = UserRecommendations.objects.filter(user=user).first()
        if rec:
            return rec.novel_ids

        recommendations = []

        UserInterest_topGenre = UserInterest.objects.filter(
            user=user, genre__isnull=False
        ).order_by("-score")[:3]

        top_tags = UserInterest.objects.filter(
            user=user, tag__isnull=False
        ).order_by("-score")[:5]

        top_genre_list = [g.genre for g in UserInterest_topGenre]
        print(top_genre_list)
        top_tags_list = [t.tag for t in top_tags]
        # 1️⃣ Personalized
        personalized1 = Novel.objects.filter(
            genres__in=top_genre_list,
            isPublic=True
        ).exclude(
            useraction__user=user,
            useraction__action='finish'
        ).distinct()

        personalized2 = Novel.objects.filter(
            tags__in=top_tags_list,
            isPublic = True
        ).exclude(
            useraction__user=user,
            useraction__action ='finish'
        ).distinct()

        recommendations.extend(personalized1)
        recommendations.extend(personalized2)

        trending = Novel.objects.exclude(
            id__in=[n.id for n in recommendations]
        ).order_by("-popularity_score").filter(isPublic=True)
        print(trending)
        recommendations.extend(trending)

        new = Novel.objects.exclude(
            id__in=[n.id for n in recommendations]
        ).order_by("-created_at")
        recommendations.extend(new)
    
        seen = set()
        final = []
        for n in recommendations:
            if n.id not in seen:
                seen.add(n.id)
                final.append(n)
            if len(final) == limit:
                break

        print(final)
        rec = UserRecommendations.objects.create(user=user,novel_ids=[n.id for n in final])
        return rec.novel_ids
    # except:
    #     return None