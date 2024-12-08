from datlich.models import Like, UserModel, Article

class LikeService:
    def create_like(self,article_id, user_id):
        user = UserModel.objects.get(id=user_id)
        article = Article.objects.get(id=article_id)
        like = Like.objects.create(
            user=user, article=article
        )
        article.like_count = article.likes.count()
        article.save()
        return like
    def delete_like(self,article_id, user_id):
        article = Article.objects.get(id=article_id)
        like = Like.objects.get( user_id=user_id, article_id=article_id )
        like.delete()
        article.like_count = article.likes.count()
        article.save()