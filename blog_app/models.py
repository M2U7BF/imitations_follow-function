from email.policy import default
from django.db import models
from django.utils.timezone import now
# (https://office54.net/python/django/model-app-import)
from users.models import *
import uuid

# Create your models here.
# 記事
class ArticleModel(models.Model):
    # 投稿者
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='投稿者')
    # 投稿内容
    posted_text = models.CharField(max_length=200,default="テキスト")
    # 投稿日時
    posted_at = models.DateTimeField(default=now, blank=True)
    #(https://self-methods.com/django-model-uuid-id/)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.posted_text[:10]