from datlich.models import Article, UserModel
from datetime import datetime, timedelta

class ArticleService:
    def get_alls(self, id):
        articles =  Article.objects.select_related('author').all()
        for article in articles:
            article.my_like = article.likes.filter(user_id=id).exists()
            comments = article.comments.select_related('user').all()
            article.list_comments = comments
        return articles
    def get_one_articles(self,id):
        article = Article.objects.get(id=id)
        return article
    def create_article(self,data, author_id):
        user = UserModel.objects.get(id = author_id)
        article = Article.objects.create(
                title=data["title"],
                content=data["content"],
                image=data["image"],
                author=user
            )
        return article