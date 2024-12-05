from datlich.models import Article, UserModel
from datetime import datetime, timedelta

class ArticleService:
    def get_alls(self):
        return Article.objects.select_related('author').all()
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