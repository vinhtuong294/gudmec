from django.db import models
from ..models import *
from django.contrib.auth.models import User

class ArticleRepository(models.Manager):
    def find_by_title_containing(self, title):
        """Tìm bài viết có chứa tiêu đề"""
        return self.filter(title__icontains=title)

    def find_by_content_containing(self, content):
        """Tìm bài viết có chứa nội dung"""
        return self.filter(content__icontains=content)

    def find_by_author(self, author):
        """Tìm bài viết theo tác giả"""
        return self.filter(author=author)

    def find_by_status(self, status):
        """Tìm bài viết theo trạng thái"""
        return self.filter(status=status)

    def find_top_3_latest(self):
        """Lấy 3 bài viết mới nhất"""
        return self.order_by('-created_at')[:3]

    def find_all(self):
        """Lấy tất cả bài viết"""
        return self.all()

# Đảm bảo rằng Article sử dụng custom repository
class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)

    objects = ArticleRepository()  # Sử dụng custom repository

    def __str__(self):
        return self.title
