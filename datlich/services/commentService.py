from datlich.models import Comment, UserModel, Article

class CommentService:
    def get_all_comments(self):
        return Comment.objects.all()
    def get_comment_articles(self,id):
        comment = Comment.objects.filter(article_id=id).order_by('-id')
        return comment
    def create_comment(self,article_id, user_id, content):
        user = UserModel.objects.get(id=user_id)
        article = Article.objects.get(id=article_id)
        print(content)
        comment = Comment.objects.create(
            user=user, article=article, content = content
        )
        return comment